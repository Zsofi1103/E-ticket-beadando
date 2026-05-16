from flask import render_template, redirect, url_for, flash, request, session, send_file, jsonify
from WebApp import db, app
from WebApp.forms.eventform import EventForm
from WebApp.forms.authforms import RegistrationForm, LoginForm, ProfileForm
from WebApp.forms.categoryform import CategoryForm
from WebApp.forms.reservationform import ReservationForm
from WebApp.forms.eventtimeform import EventTimeForm
from WebApp.managers.eventmanager import EventManager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from WebApp.models.user import User
from WebApp.models.reservation import Reservation
from WebApp.models.event import Event
from WebApp.models.event_time import EventTime
from datetime import datetime
from WebApp.forms.reservationform import ReservationForm as CSRFForm
from sqlalchemy import func

em = EventManager(db)


def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    try:
        return db.session.get(User, uid)
    except Exception as e:
        app.logger.error('Could not load current user from DB: %s', e)
        return None


def admin_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin():
            flash('Admin jogosultság szükséges.', 'hiba')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)

    return wrapper


@app.route('/')
def index():
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    category_id = request.args.get('category')
    q = request.args.get('q')
    if category_id:
        try:
            category_id = int(category_id)
        except Exception:
            category_id = None

    page_res = em.list_events(page=page, per_page=per_page, category_id=category_id, q=q)
    events = page_res['items']
    top = em.top_events(limit=5)
    user = None
    if session.get('user_id'):
        user = db.session.get(User, session.get('user_id'))
    is_admin = user.is_admin() if user else False
    from WebApp.models.category import Category
    categories = db.session.query(Category).order_by(Category.name).all()
    csfr_form = ReservationForm()
    return render_template('index.html', events=events, is_admin=is_admin, page_res=page_res, categories=categories, selected_category=category_id, q=q, csrf_form=csfr_form, top_events=top)


@app.context_processor
def inject_user():
    try:
        user = get_current_user()
        return {
            'current_user': user,
            'current_user_name': user.name if user else None,
            'is_admin': user.is_admin() if user else False,
        }
    except Exception:
        return {'current_user': None, 'current_user_name': None, 'is_admin': False}


@app.route('/event/new', methods=['GET', 'POST'])
@admin_required
def event_new():
    from WebApp.models.category import Category
    form = EventForm()
    try:
        cats = db.session.query(Category).order_by(Category.name).all()
        form.category_id.choices = [(0, '— Nincs kategória —')] + [(c.id, c.name) for c in cats]
    except Exception:
        db.session.rollback()
        flash('Hiba a kategóriák betöltése közben. Próbáld újra később.', 'hiba')
        return redirect(url_for('index'))
    try:
        from WebApp.models.venue import Venue
        venues = db.session.query(Venue).order_by(func.lower(Venue.name)).all()
        form.venue_id.choices = [(0, '— Nincs helyszín —')] + [(v.id, v.name) for v in venues]
    except Exception:
        db.session.rollback()

    try:
        if form.validate_on_submit():
            e = Event(title=form.title.data, description=form.description.data)
            try:
                if getattr(form, 'price', None) and form.price.data is not None and str(form.price.data) != '':
                    e.price = form.price.data
            except Exception:
                e.price = None
            sel = None
            try:
                if form.category_id.data and int(form.category_id.data) != 0:
                    sel = db.session.get(Category, int(form.category_id.data))
            except Exception:
                sel = None
            if sel:
                e.categories.append(sel)
            if form.start_at.data:
                try:
                    s = form.start_at.data
                    if 'T' in s:
                        e.start_at = datetime.strptime(s, '%Y-%m-%dT%H:%M')
                    else:
                        e.start_at = datetime.strptime(s, '%Y-%m-%d %H:%M')
                except Exception:
                    e.start_at = None
            try:
                sel_v = None
                if getattr(form, 'venue_id', None) and int(form.venue_id.data) != 0:
                    from WebApp.models.venue import Venue
                    sel_v = db.session.get(Venue, int(form.venue_id.data))
            except Exception:
                sel_v = None
            if sel_v:
                e.venue = sel_v
            db.session.add(e)
            db.session.commit()
            flash(f'({e.id}) {e.title} esemény elmentve.', 'sikeres')
            return redirect(url_for('index'))
    except Exception:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        flash('Váratlan hiba történt az esemény mentésekor. Ellenőrizd a naplót.', 'hiba')
        return redirect(url_for('index'))

    return render_template('event/new_edit.html', form=form, add=True)


@app.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@admin_required
def event_edit(event_id: int):
    from WebApp.models.event import Event
    event = db.session.get(Event, event_id)
    if not event:
        flash('Nincs ilyen esemény.', 'hiba')
        return redirect(url_for('index'))
    from WebApp.models.category import Category
    form = EventForm(obj=event)
    try:
        cats = db.session.query(Category).order_by(Category.name).all()
        form.category_id.choices = [(0, '— Nincs kategória —')] + [(c.id, c.name) for c in cats]
    except Exception:
        db.session.rollback()
        flash('Hiba a kategóriák betöltése közben. Próbáld újra később.', 'hiba')
        return redirect(url_for('index'))
    try:
        from WebApp.models.venue import Venue
        venues = db.session.query(Venue).order_by(func.lower(Venue.name)).all()
        form.venue_id.choices = [(0, '— Nincs helyszín —')] + [(v.id, v.name) for v in venues]
    except Exception:
        db.session.rollback()
        flash('Hiba a helyszínek betöltése közben. Próbáld újra később.', 'hiba')
        return redirect(url_for('index'))
    if request.method == 'GET':
        if event.categories and len(event.categories) > 0:
            form.category_id.data = event.categories[0].id
        else:
            form.category_id.data = 0
        try:
            if event.start_at:
                form.start_at.data = event.start_at.strftime('%Y-%m-%dT%H:%M')
            else:
                try:
                    first_time = db.session.query(EventTime).filter_by(event_id=event.id).order_by(EventTime.year, EventTime.month, EventTime.day, EventTime.hour, EventTime.minute).first()
                    if first_time:
                        dt = datetime(first_time.year, first_time.month, first_time.day, first_time.hour, first_time.minute)
                        form.start_at.data = dt.strftime('%Y-%m-%dT%H:%M')
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if getattr(event, 'price', None) is not None:
                form.price.data = float(event.price)
        except Exception:
            pass
        try:
            form.venue_id.data = int(event.venue_id) if getattr(event, 'venue_id', None) else 0
        except Exception:
            form.venue_id.data = 0
    try:
        if form.validate_on_submit():
            event.title = form.title.data
            event.description = form.description.data
            if form.start_at.data:
                try:
                    s = form.start_at.data
                    if 'T' in s:
                        event.start_at = datetime.strptime(s, '%Y-%m-%dT%H:%M')
                    else:
                        event.start_at = datetime.strptime(s, '%Y-%m-%d %H:%M')
                except Exception:
                    event.start_at = None
            sel = None
            try:
                if form.category_id.data and int(form.category_id.data) != 0:
                    sel = db.session.get(Category, int(form.category_id.data))
            except Exception:
                sel = None
            if sel:
                event.categories = [sel]
            else:
                event.categories = []
            try:
                sel_v = None
                if getattr(form, 'venue_id', None) and int(form.venue_id.data) != 0:
                    from WebApp.models.venue import Venue
                    sel_v = db.session.get(Venue, int(form.venue_id.data))
            except Exception:
                sel_v = None
            if sel_v:
                event.venue = sel_v
            else:
                event.venue = None
            try:
                if getattr(form, 'price', None) and form.price.data is not None and str(form.price.data) != '':
                    event.price = form.price.data
                else:
                    event.price = None
            except Exception:
                event.price = None
            db.session.commit()
            flash('Esemény frissítve.', 'sikeres')
            return redirect(url_for('event_detail', event_id=event.id))
    except Exception:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        flash('Váratlan hiba történt az esemény frissítésekor.', 'hiba')
        return redirect(url_for('index'))
    return render_template('event/new_edit.html', form=form, add=False)


@app.route('/event/delete/<int:event_id>', methods=['POST'])
@admin_required
def event_delete(event_id: int):
    from WebApp.models.event import Event
    form = ReservationForm()
    if not form.validate_on_submit():
        flash('Érvénytelen kérelem (hiányzó CSRF vagy űrlap).', 'hiba')
        return redirect(url_for('index'))
    event = db.session.get(Event, event_id)
    if not event:
        flash('Nincs ilyen esemény.', 'hiba')
        return redirect(url_for('index'))
    if getattr(event, 'reservations', None) and len(event.reservations) > 0:
        flash('Az esemény nem törölhető, amíg van rá foglalás.', 'hiba')
        return redirect(url_for('event_detail', event_id=event.id))
    if getattr(event, 'categories', None) and len(event.categories) > 0:
        flash('Az esemény nem törölhető, amíg kategóriához tartozik.', 'hiba')
        return redirect(url_for('event_detail', event_id=event.id))
    try:
        if getattr(event, 'times', None) and len(event.times) > 0:
            flash('Az esemény nem törölhető, amíg rajta vannak időpontok.', 'hiba')
            return redirect(url_for('event_detail', event_id=event.id))
    except Exception:
        flash('Az esemény nem törölhető jelenleg (időpontok lekérése sikertelen).', 'hiba')
        return redirect(url_for('event_detail', event_id=event.id))
    try:
        if getattr(event, 'venue_id', None) is not None and event.venue_id:
            flash('Az esemény nem törölhető, amíg van hozzá rendelt helyszín.', 'hiba')
            return redirect(url_for('event_detail', event_id=event.id))
    except Exception:
        flash('Az esemény törlése jelenleg nem engedélyezett (helyszín ellenőrzése sikertelen).', 'hiba')
        return redirect(url_for('event_detail', event_id=event.id))
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Esemény törölve.', 'sikeres')
    except Exception:
        db.session.rollback()
        flash('Hiba az esemény törlésekor.', 'hiba')
    return redirect(url_for('index'))


@app.route('/event/detail/<int:event_id>')
def event_detail(event_id: int):
    event = em.get_event(event_id)
    form = ReservationForm()
    times = []
    try:
        times = db.session.query(EventTime).filter_by(event_id=event.id).order_by(EventTime.year, EventTime.month, EventTime.day, EventTime.hour, EventTime.minute).all()
    except Exception as ex:
        app.logger.debug('Could not load EventTime rows: %s', ex)
        times = []
    return render_template('event/detail.html', event=event, reservation_form=form, times=times)


@app.route('/api/events')
def api_events():
    try:
        events = db.session.query(Event).all()
        out = []
        for e in events:
            try:
                categories = [{'id': c.id, 'name': c.name} for c in (e.categories or [])]
            except Exception:
                categories = []
            try:
                reservations = [
                    {'id': r.id, 'user_id': r.user_id, 'created_at': r.created_at.isoformat() if r.created_at else None}
                    for r in (e.reservations or [])
                ]
            except Exception:
                reservations = []
            try:
                venue = None
                if getattr(e, 'venue', None):
                    v = e.venue
                    venue = {'id': v.id, 'name': v.name, 'address': v.address, 'capacity': v.capacity}
            except Exception:
                venue = None
            out.append({
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'created_at': e.created_at.isoformat() if getattr(e, 'created_at', None) else None,
                'start_at': e.start_at.isoformat() if getattr(e, 'start_at', None) else None,
                'price': float(e.price) if getattr(e, 'price', None) is not None else None,
                'categories': categories,
                'reservations': reservations,
                'venue': venue,
            })
        return jsonify({'events': out}), 200
    except Exception as ex:
        app.logger.exception('Could not build events API response: %s', ex)
        return jsonify({'error': 'Could not retrieve events'}), 500


@app.route('/event/<int:event_id>/time/new', methods=['GET', 'POST'])
@admin_required
def event_time_new(event_id: int):
    from WebApp.models.event import Event
    event = db.session.get(Event, event_id)
    if not event:
        flash('Nincs ilyen esemény.', 'hiba')
        return redirect(url_for('index'))
    form = EventTimeForm()
    if form.validate_on_submit():
        et = EventTime(
            event_id=event.id,
            year=int(form.year.data),
            month=int(form.month.data),
            day=int(form.day.data),
            hour=int(form.hour.data),
            minute=int(form.minute.data),
        )
        try:
            db.session.add(et)
            db.session.commit()
            flash('Időpont hozzáadva.', 'sikeres')
            return redirect(url_for('event_detail', event_id=event.id))
        except Exception:
            db.session.rollback()
            flash('Hiba az időpont mentésekor.', 'hiba')
    return render_template('event/time_form.html', form=form, event=event, add=True)


@app.route('/event/<int:event_id>/time/edit/<int:time_id>', methods=['GET', 'POST'])
@admin_required
def event_time_edit(event_id: int, time_id: int):
    et = db.session.get(EventTime, time_id)
    if not et or et.event_id != event_id:
        flash('Nincs ilyen időpont.', 'hiba')
        return redirect(url_for('index'))
    form = EventTimeForm(obj=et)
    if form.validate_on_submit():
        et.year = int(form.year.data)
        et.month = int(form.month.data)
        et.day = int(form.day.data)
        et.hour = int(form.hour.data)
        et.minute = int(form.minute.data)
        try:
            db.session.commit()
            flash('Időpont frissítve.', 'sikeres')
            return redirect(url_for('event_detail', event_id=event_id))
        except Exception:
            db.session.rollback()
            flash('Hiba az időpont mentésekor.', 'hiba')
    return render_template('event/time_form.html', form=form, event=et.event, add=False, et=et)


@app.route('/event/<int:event_id>/time/delete/<int:time_id>', methods=['POST'])
@admin_required
def event_time_delete(event_id: int, time_id: int):
    # reuse ReservationForm for CSRF
    form = ReservationForm()
    if not form.validate_on_submit():
        flash('Érvénytelen kérelem (hiányzó CSRF vagy űrlap).', 'hiba')
        return redirect(url_for('event_detail', event_id=event_id))
    et = db.session.get(EventTime, time_id)
    if not et or et.event_id != event_id:
        flash('Nincs ilyen időpont.', 'hiba')
        return redirect(url_for('index'))
    try:
        db.session.delete(et)
        db.session.commit()
        flash('Időpont törölve.', 'sikeres')
    except Exception:
        db.session.rollback()
        flash('Hiba az időpont törlésekor.', 'hiba')
    return redirect(url_for('event_detail', event_id=event_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # server-side check: password must not contain spaces
        if ' ' in form.password.data:
            flash('A jelszó nem tartalmazhat szóközöket.', 'hiba')
            return render_template('auth/register.html', form=form)

        # ensure password and confirmation match (defensive check)
        if form.password.data != form.password2.data:
            flash('A jelszavak nem egyeznek.', 'hiba')
            return render_template('auth/register.html', form=form)
        # check email unique (use scalar to retrieve User or None)
        existing = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if existing is not None:
            flash('Ezzel az e-mail címmel már regisztráltak.', 'hiba')
            return render_template('auth/register.html', form=form)
        user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role='user'
        )
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Hiba a regisztráció során.', 'hiba')
            return render_template('auth/register.html', form=form)
        session['user_id'] = user.id
        flash('Sikeres regisztráció, be vagy jelentkezve.', 'sikeres')
        return redirect(url_for('index'))
    return render_template('auth/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # disallow spaces in password input
        if ' ' in form.password.data:
            flash('A jelszó nem tartalmazhat szóközöket.', 'hiba')
            return render_template('auth/login.html', form=form)
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Ismeretlen e-mail vagy hibás jelszó.', 'hiba')
            return render_template('auth/login.html', form=form)
        session['user_id'] = user.id
        flash('Sikeres bejelentkezés.', 'sikeres')
        return redirect(url_for('index'))
    return render_template('auth/login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Kijelentkeztél.', 'sikeres')
    return redirect(url_for('index'))


@app.route('/categories')
@admin_required
def category_list():
    # pagination
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    q = request.args.get('q')
    from WebApp.models.category import Category
    query = db.session.query(Category).order_by(Category.name)
    if q:
        query = query.filter(Category.name.ilike(f"%{q}%"))
    total = query.count()
    pages = (total + per_page - 1) // per_page if per_page else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    page_res = {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
    # provide a CSRF form to use in delete forms
    csrf_form = ReservationForm()
    return render_template('category/list.html', categories=items, page_res=page_res, q=q, csrf_form=csrf_form)


@app.route('/venues')
def venue_list():
    # public paginated list of venues with optional search
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    q = request.args.get('q')
    from WebApp.models.venue import Venue
    query = db.session.query(Venue).order_by(Venue.name)
    if q:
        qlike = f"%{q}%"
        query = query.filter((Venue.name.ilike(qlike)) | (Venue.address.ilike(qlike)))
    total = query.count()
    pages = (total + per_page - 1) // per_page if per_page else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    page_res = {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
    csrf_form = ReservationForm()
    return render_template('venues.html', venues=items, page_res=page_res, q=q, csrf_form=csrf_form)


@app.route('/admin/venues')
@admin_required
def admin_venues():
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    q = request.args.get('q')
    from WebApp.models.venue import Venue
    query = db.session.query(Venue).order_by(Venue.name)
    if q:
        qlike = f"%{q}%"
        query = query.filter((Venue.name.ilike(qlike)) | (Venue.address.ilike(qlike)))
    total = query.count()
    pages = (total + per_page - 1) // per_page if per_page else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    page_res = {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
    csrf_form = ReservationForm()
    return render_template('admin/venues_list.html', venues=items, page_res=page_res, q=q, csrf_form=csrf_form)


@app.route('/admin/venue/new', methods=['GET', 'POST'])
@admin_required
def admin_venue_new():
    from WebApp.forms.venueform import VenueForm
    form = VenueForm()
    if form.validate_on_submit():
        from WebApp.models.venue import Venue
        # check uniqueness (case-insensitive)
        from sqlalchemy import func
        name_val = form.name.data.strip()
        existing = db.session.scalar(db.select(Venue).filter(func.lower(Venue.name) == name_val.lower()))
        if existing is not None:
            form.name.errors.append('Ezzel a névvel már létezik helyszín.')
            return render_template('admin/venue_form.html', form=form, add=True)

        v = Venue(name=name_val, address=form.address.data.strip() if form.address.data else None, capacity=form.capacity.data)
        try:
            db.session.add(v)
            db.session.commit()
            flash('Helyszín létrehozva.', 'sikeres')
            return redirect(url_for('admin_venues'))
        except Exception as ex:
            db.session.rollback()
            app.logger.error('Could not create venue: %s', ex)
            flash('Hiba a helyszín létrehozásakor. Ellenőrizd az adatokat.', 'hiba')
    return render_template('admin/venue_form.html', form=form, add=True)


@app.route('/admin/venue/edit/<int:venue_id>', methods=['GET', 'POST'])
@admin_required
def admin_venue_edit(venue_id: int):
    from WebApp.models.venue import Venue
    from WebApp.forms.venueform import VenueForm
    v = db.session.get(Venue, venue_id)
    if not v:
        flash('Nincs ilyen helyszín.', 'hiba')
        return redirect(url_for('admin_venues'))
    form = VenueForm(obj=v)
    if form.validate_on_submit():
        name_val = form.name.data.strip()
        # ensure no other venue uses this name (case-insensitive)
        from sqlalchemy import func
        conflict = db.session.scalar(db.select(Venue).filter(func.lower(Venue.name) == name_val.lower(), Venue.id != v.id))
        if conflict is not None:
            form.name.errors.append('Ezzel a névvel már létezik másik helyszín.')
            return render_template('admin/venue_form.html', form=form, add=False)

        v.name = name_val
        v.address = form.address.data.strip() if form.address.data else None
        v.capacity = form.capacity.data
        try:
            db.session.commit()
            flash('Helyszín frissítve.', 'sikeres')
            return redirect(url_for('admin_venues'))
        except Exception as ex:
            db.session.rollback()
            app.logger.error('Could not update venue: %s', ex)
            flash('Hiba a helyszín mentésekor.', 'hiba')
    return render_template('admin/venue_form.html', form=form, add=False)


@app.route('/admin/venue/delete/<int:venue_id>', methods=['POST'])
@admin_required
def admin_venue_delete(venue_id: int):
    from WebApp.models.venue import Venue
    form = ReservationForm()
    if not form.validate_on_submit():
        flash('Érvénytelen kérelem (hiányzó CSRF vagy űrlap).', 'hiba')
        return redirect(url_for('admin_venues'))
    v = db.session.get(Venue, venue_id)
    if not v:
        flash('Nincs ilyen helyszín.', 'hiba')
        return redirect(url_for('admin_venues'))
    # prevent delete if referenced by events
    if getattr(v, 'events', None) and len(v.events) > 0:
        flash('A helyszín nem törölhető, amíg esemény hivatkozik rá.', 'hiba')
        return redirect(url_for('admin_venues'))
    try:
        db.session.delete(v)
        db.session.commit()
        flash('Helyszín törölve.', 'sikeres')
    except Exception as ex:
        db.session.rollback()
        app.logger.error('Could not delete venue: %s', ex)
        flash('Hiba a helyszín törlésekor.', 'hiba')
    return redirect(url_for('admin_venues'))


@app.route('/admin/reservations')
@admin_required
def admin_reservations():
    from WebApp.models.reservation import Reservation
    # pagination and optional search
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    q = request.args.get('q')
    query = db.session.query(Reservation).join(Reservation.user).join(Reservation.event).order_by(Reservation.created_at.desc())
    if q:
        query = query.filter((User.email.ilike(f"%{q}%")) | (Event.title.ilike(f"%{q}%")))
    total = query.count()
    pages = (total + per_page - 1) // per_page if per_page else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    page_res = {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
    csrf_form = ReservationForm()
    return render_template('admin/reservations.html', reservations=items, page_res=page_res, csrf_form=csrf_form, q=q)


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Simple admin dashboard that links to common admin pages."""
    from WebApp.models.category import Category
    # Reservation is already imported near top
    try:
        cat_count = db.session.query(Category).count()
    except Exception:
        db.session.rollback()
        cat_count = 0
    try:
        res_count = db.session.query(Reservation).count()
    except Exception:
        db.session.rollback()
        res_count = 0
    try:
        # event count for admin dashboard
        from WebApp.models.event import Event
        event_count = db.session.query(Event).count()
    except Exception:
        db.session.rollback()
        event_count = 0
    return render_template('admin/dashboard.html', cat_count=cat_count, res_count=res_count, event_count=event_count)


@app.route('/category/new', methods=['GET', 'POST'])
@admin_required
def category_new():
    form = CategoryForm()
    if form.validate_on_submit():
        from WebApp.models.category import Category
        c = Category(name=form.name.data)
        db.session.add(c)
        db.session.commit()
        flash('Kategória létrehozva.', 'sikeres')
        return redirect(url_for('category_list'))
    return render_template('category/new_edit.html', form=form, add=True)


@app.route('/category/edit/<int:cat_id>', methods=['GET', 'POST'])
@admin_required
def category_edit(cat_id):
    from WebApp.models.category import Category
    c = db.session.get(Category, cat_id)
    if not c:
        flash('Nincs ilyen kategória.', 'hiba')
        return redirect(url_for('category_list'))
    form = CategoryForm(obj=c)
    if form.validate_on_submit():
        c.name = form.name.data
        db.session.commit()
        flash('Kategória frissítve.', 'sikeres')
        return redirect(url_for('category_list'))
    return render_template('category/new_edit.html', form=form, add=False)


@app.route('/category/delete/<int:cat_id>', methods=['POST'])
@admin_required
def category_delete(cat_id):
    from WebApp.models.category import Category
    c = db.session.get(Category, cat_id)
    if not c:
        flash('Nincs ilyen kategória.', 'hiba')
        return redirect(url_for('category_list'))
    # prevent deletion if referenced
    if c.events:
        flash('A kategória nem törölhető, amíg esemény hivatkozik rá.', 'hiba')
        return redirect(url_for('category_list'))
    db.session.delete(c)
    db.session.commit()
    flash('Kategória törölve.', 'sikeres')
    return redirect(url_for('category_list'))


@app.route('/profile')
def profile():
    user = get_current_user()
    if not user:
        flash('Jelentkezz be a profil megtekintéséhez.', 'hiba')
        return redirect(url_for('login'))
    # paginated list of user's reservations
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    query = db.session.query(Reservation).filter_by(user_id=user.id).order_by(Reservation.created_at.desc())
    total = query.count()
    pages = (total + per_page - 1) // per_page if per_page else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    page_res = {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
    form = ReservationForm()
    return render_template('auth/profile.html', user=user, reservations=items, reservation_form=form, page_res=page_res)


@app.route('/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    user = get_current_user()
    if not user:
        flash('Jelentkezz be a profil szerkesztéséhez.', 'hiba')
        return redirect(url_for('login'))
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        # update name
        user.name = form.name.data
        # handle password change if requested
        if form.new_password.data:
            # current password must match
            if not form.current_password.data or not check_password_hash(user.password_hash, form.current_password.data):
                flash('A jelenlegi jelszó hibás.', 'hiba')
                return render_template('auth/edit_profile.html', form=form)
            # warn if new password equals current
            if check_password_hash(user.password_hash, form.new_password.data):
                flash('Az új jelszó megegyezik a jelenlegi jelszóval. Válassz másikat.', 'hiba')
                return render_template('auth/edit_profile.html', form=form)
            # set new hash
            user.password_hash = generate_password_hash(form.new_password.data)
        try:
            db.session.commit()
            flash('Profil frissítve.', 'sikeres')
            return redirect(url_for('profile'))
        except Exception:
            db.session.rollback()
            flash('Hiba a profil mentésekor.', 'hiba')
    return render_template('auth/edit_profile.html', form=form)


def _get_serializer():
    return URLSafeTimedSerializer(app.config.get('SECRET_KEY', 'secret-key'))


@app.route('/password-reset/request', methods=['GET', 'POST'])
def password_reset_request():
    from WebApp.forms.authforms import PasswordResetRequestForm
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.scalar(db.select(User).filter_by(email=email))
        if user:
            s = _get_serializer()
            token = s.dumps(user.email, salt='password-reset-salt')
            reset_url = url_for('password_reset', token=token, _external=True)
            # In production, send email. For now, show the link as a debug flash and print.
            flash('Password reset link (development): ' + reset_url, 'sikeres')
            print('Password reset link for', user.email, ':', reset_url)
        else:
            # do not reveal existence
            flash('Ha van ilyen fiók, küldtünk reset linket az e-mailre.', 'sikeres')
        return redirect(url_for('login'))
    return render_template('auth/password_reset_request.html', form=form)


@app.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    from WebApp.forms.authforms import PasswordResetForm
    s = _get_serializer()
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('A visszaállító link lejárt.', 'hiba')
        return redirect(url_for('password_reset_request'))
    except BadSignature:
        flash('Érvénytelen visszaállító link.', 'hiba')
        return redirect(url_for('password_reset_request'))
    user = db.session.scalar(db.select(User).filter_by(email=email))
    if not user:
        flash('Érvénytelen felhasználó.', 'hiba')
        return redirect(url_for('password_reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        # prevent reusing same password
        if check_password_hash(user.password_hash, form.new_password.data):
            flash('Az új jelszó megegyezik a jelenlegi jelszóval. Válassz másikat.', 'hiba')
            return render_template('auth/password_reset.html', form=form)
        user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Jelszó sikeresen frissítve. Jelentkezz be az új jelszóval.', 'sikeres')
        return redirect(url_for('login'))
    return render_template('auth/password_reset.html', form=form)


@app.route('/event/<int:event_id>/reserve', methods=['POST'])
def reserve_event(event_id: int):
    user = get_current_user()
    if not user:
        flash('Előbb jelentkezz be a foglaláshoz.', 'hiba')
        return redirect(url_for('login'))
    form = ReservationForm()
    if not form.validate_on_submit():
        flash('Érvénytelen kérelem (hiányzó CSRF vagy űrlap).', 'hiba')
        return redirect(url_for('event_detail', event_id=event_id))
    # check event exists
    from WebApp.models.event import Event
    event = db.session.get(Event, event_id)
    if not event:
        flash('Nincs ilyen esemény.', 'hiba')
        return redirect(url_for('index'))
    # ensure not already reserved
    existing = db.session.scalar(db.select(Reservation).filter_by(event_id=event_id, user_id=user.id))
    if existing:
        flash('Már van foglalásod erre az eseményre.', 'hiba')
        return redirect(url_for('event_detail', event_id=event_id))
    res = Reservation(event_id=event_id, user_id=user.id)
    try:
        db.session.add(res)
        db.session.commit()
        flash('Sikeres foglalás.', 'sikeres')
    except Exception:
        db.session.rollback()
        flash('Hiba a foglalás során.', 'hiba')
    return redirect(url_for('event_detail', event_id=event_id))


@app.route('/event/<int:event_id>/favorite', methods=['POST'])
def toggle_favorite(event_id: int):
    user = get_current_user()
    if not user:
        flash('Jelentkezz be a kedvencek kezeléséhez.', 'hiba')
        return redirect(url_for('login'))
    form = CSRFForm()
    if not form.validate_on_submit():
        flash('Érvénytelen kérelem (hiányzó CSRF).', 'hiba')
        return redirect(url_for('event_detail', event_id=event_id))
    # ensure event exists
    ev = db.session.get(Event, event_id)
    if not ev:
        flash('Nincs ilyen esemény.', 'hiba')
        return redirect(url_for('index'))
    try:
        # check membership via relationship
        if ev in user.favorites:
            # remove
            user.favorites.remove(ev)
            db.session.commit()
            flash('Esemény eltávolítva a kedvenceid közül.', 'sikeres')
        else:
            user.favorites.append(ev)
            db.session.commit()
            flash('Esemény hozzáadva a kedvenceidhez.', 'sikeres')
    except Exception:
        db.session.rollback()
        flash('Hiba a kedvencek mentésekor.', 'hiba')
    return redirect(url_for('event_detail', event_id=event_id))


@app.route('/favorites')
def favorites():
    user = get_current_user()
    if not user:
        flash('Jelentkezz be a kedvencek megtekintéséhez.', 'hiba')
        return redirect(url_for('login'))
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    # query events favorited by the user
    from WebApp.models.event import favorites as favorites_table
    query = db.session.query(Event).join(favorites_table).filter(favorites_table.c.user_id == user.id).order_by(Event.created_at.desc())
    total = query.count()
    pages = (total + per_page - 1) // per_page if per_page else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    page_res = {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
    # small CSRF form for actions
    csrf_form = CSRFForm()
    return render_template('favorites.html', events=items, page_res=page_res, csrf_form=csrf_form)


@app.route('/reservation/delete/<int:res_id>', methods=['POST'])
def reservation_delete(res_id: int):
    user = get_current_user()
    if not user:
        flash('Előbb jelentkezz be a foglalás törléséhez.', 'hiba')
        return redirect(url_for('login'))
    form = ReservationForm()
    if not form.validate_on_submit():
        flash('Érvénytelen kérelem (hiányzó CSRF vagy űrlap).', 'hiba')
        return redirect(url_for('profile'))

    r = db.session.get(Reservation, res_id)
    if not r:
        flash('Nincs ilyen foglalás.', 'hiba')
        return redirect(url_for('profile'))
    # only owner or admin can delete
    if r.user_id != user.id and not user.is_admin():
        flash('Nincs jogosultságod törölni ezt a foglalást.', 'hiba')
        return redirect(url_for('profile'))
    try:
        db.session.delete(r)
        db.session.commit()
        flash('Foglalás törölve.', 'sikeres')
    except Exception:
        db.session.rollback()
        flash('Hiba a foglalás törlésekor.', 'hiba')
    return redirect(url_for('profile'))


@app.errorhandler(Exception)
def handle_exception(e):
    # Distinguish HTTP exceptions (404/403/etc) from internal errors.
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        # Let Flask handle HTTP exceptions (shows correct status code/page)
        return e

    # Log full traceback for unexpected exceptions
    import traceback
    tb = traceback.format_exc()
    app.logger.error('Unhandled exception: %s', tb)
    # In development show the traceback in the response for easier debugging
    from os import environ
    if environ.get('FLASK_ENV') == 'development' or environ.get('DEBUG') == '1':
        return f"<h1>Internal Server Error</h1><pre>{tb}</pre>", 500
    # Otherwise show friendly message and redirect to index (and log is available in admin logs)
    flash('Váratlan hiba történt a szerveren. Ellenőrizd a naplót.', 'hiba')
    return redirect(url_for('index'))


@app.route('/_admin/logs')
def admin_logs():
    """Return last part of flask_errors.log for admins (development helper)."""
    user = get_current_user()
    if not user or not user.is_admin():
        flash('Admin jogosultság szükséges a naplók megtekintéséhez.', 'hiba')
        return redirect(url_for('index'))
    import os
    log_path = os.path.join(app.root_path, '..', 'flask_errors.log')
    if not os.path.exists(log_path):
        flash('Naplófájl nem található.', 'hiba')
        return redirect(url_for('admin_dashboard'))
    # read last ~400 lines
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read().splitlines()
    tail_lines = data[-400:]
    tail = '\n'.join(tail_lines)
    return render_template('admin/logs.html', tail=tail)


@app.route('/_admin/logs/download')
def admin_logs_download():
    user = get_current_user()
    if not user or not user.is_admin():
        flash('Admin jogosultság szükséges a naplók letöltéséhez.', 'hiba')
        return redirect(url_for('index'))
    import os
    log_path = os.path.join(app.root_path, '..', 'flask_errors.log')
    if not os.path.exists(log_path):
        flash('Naplófájl nem található.', 'hiba')
        return redirect(url_for('admin_dashboard'))
    return send_file(log_path, as_attachment=True, download_name='flask_errors.log')