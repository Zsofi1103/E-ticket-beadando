import re
from WebApp import app, db
from WebApp.models.event import Event
from WebApp.models.reservation import Reservation

MIGRATION_PATH = 'migrations/versions/1272d8bf8638_event_entity_added.py'
BACKUP_JSON = 'eticket_dump_before_restore.json'


def parse_events_from_migration(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # find the INSERT INTO ... VALUES ( ... ); block
    m = re.search(r"INSERT INTO event \(title, description\) VALUES\s*(\(.*?\));", text, re.S)
    if not m:
        # try to capture between triple quotes op.execute(""" ... """)
        m2 = re.search(r"op.execute\(\"\"\"(.*?)\"\"\"\)", text, re.S)
        block = m2.group(1) if m2 else ''
    else:
        block = m.group(1)
    if not block:
        return []
    # find all tuples like ('Title', 'Desc')
    pairs = re.findall(r"\('([^']*)'\s*,\s*'([^']*)'\)", block)
    # unescape common sequences (none expected) - return list of (title, desc)
    return pairs


def run_restore_and_clean():
    with app.app_context():
        # parse original events from migration
        original = parse_events_from_migration(MIGRATION_PATH)
        original_titles = {t for t, d in original}
        print(f'Parsed {len(original)} original events from migration')

        # insert originals if missing
        added = 0
        for title, desc in original:
            exists = db.session.scalar(db.select(Event).filter_by(title=title))
            if not exists:
                e = Event(title=title, description=desc)
                db.session.add(e)
                added += 1
        if added:
            db.session.commit()
        print(f'Inserted {added} original events (new)')

        # now remove test events: titles like E\d+ OR description == 'x', but do NOT remove events in original_titles
        import re as _re
        events = db.session.query(Event).all()
        to_delete = []
        for e in events:
            title = (e.title or '').strip()
            desc = (e.description or '').strip()
            is_test_title = bool(_re.match(r'^E\d+$', title))
            is_test_desc = (desc == 'x')
            if (is_test_title or is_test_desc) and title not in original_titles:
                to_delete.append(e)
        deleted_events = 0
        deleted_res = 0
        if to_delete:
            ids = [e.id for e in to_delete]
            # delete reservations referencing them first
            deleted_res = db.session.query(Reservation).filter(Reservation.event_id.in_(ids)).delete(synchronize_session=False)
            for e in to_delete:
                db.session.delete(e)
                deleted_events += 1
            db.session.commit()
        print(f'Deleted {deleted_events} test events and {deleted_res} reservations')


if __name__ == '__main__':
    run_restore_and_clean()
