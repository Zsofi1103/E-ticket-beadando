#!/usr/bin/env python
"""
Ensure only events with no categories are assigned the "Egyéb" category.
- Create the category if missing.
- For events with zero categories: attach Egyéb (if not already attached).
- For events that have one or more categories: remove Egyéb if present.
- Print a summary and sample lists.
Idempotent: can be run multiple times.
"""
from WebApp import db, app


def run():
    from WebApp.models.event import Event
    from WebApp.models.category import Category

    with app.app_context():

        egyeb = db.session.query(Category).filter(Category.name.ilike('egyéb')).one_or_none()
        if not egyeb:
            egyeb = Category(name='Egyéb')
            db.session.add(egyeb)
            try:
                db.session.commit()
                print('Created category: Egyéb (id=%s)' % egyeb.id)
            except Exception as ex:
                db.session.rollback()
                print('Failed creating Egyéb category:', ex)
                return
        else:
            print('Found Egyéb category id=%s' % egyeb.id)

        assigned = 0
        removed = 0
        nochange = 0
        samples_assigned = []
        samples_removed = []

        events = db.session.query(Event).order_by(Event.id.asc()).all()
        for ev in events:

            cats = list(ev.categories) if ev.categories is not None else []
            has_egyeb = any((c.name or '').strip().lower() == 'egyéb' for c in cats)
            if not cats:
                if not has_egyeb:
                    ev.categories.append(egyeb)
                    db.session.add(ev)
                    assigned += 1
                    if len(samples_assigned) < 10:
                        samples_assigned.append((ev.id, ev.title or ''))
                else:
                    nochange += 1
            else:

                if has_egyeb:

                    try:
                        ev.categories = [c for c in cats if (c.name or '').strip().lower() != 'egyéb']
                        db.session.add(ev)
                        removed += 1
                        if len(samples_removed) < 10:
                            samples_removed.append((ev.id, ev.title or '', [c.name for c in ev.categories]))
                    except Exception as ex:
                        db.session.rollback()
                        print('Error removing Egyéb from event', ev.id, ex)
                else:
                    nochange += 1
        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            print('Commit failed:', ex)
            return

       
        print('\nSummary:')
        print('  Assigned Egyéb to events with no categories:', assigned)
        print('  Removed Egyéb from events that had other categories:', removed)
        print('  Events unchanged:', nochange)

        if samples_assigned:
            print('\nSample assigned (id, title):')
            for s in samples_assigned:
                print('  ', s)
        if samples_removed:
            print('\nSample removed (id, title, remaining_categories):')
            for s in samples_removed:
                print('  ', s)

        total_with_egyeb = db.session.query(Event).join(Event.categories).filter(Category.id == egyeb.id).count()
        print('\nTotal events with Egyéb now:', total_with_egyeb)


if __name__ == '__main__':
    run()
