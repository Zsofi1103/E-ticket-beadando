#!/usr/bin/env python
"""
Remove duplicate events by title.

Rules:
- For each group of events with the same title (exact match), if any event has a non-empty description, remove those without description.
- If after that more than one remains (all have descriptions), keep the earliest-created event and delete the others.
- Reservations attached to deleted events will be removed as well.

Idempotent and prints a summary.
"""
from WebApp import db, app


def run():
    from WebApp.models.event import Event
    from WebApp.models.reservation import Reservation

    import re

    def normalize_title(t: str) -> str:
        if not t:
            return ''
        s = t.lower()
        # replace various dashes/underscores/slashes with space
        s = re.sub(r'[\-–—_/]+', ' ', s)
        # remove other punctuation
        s = re.sub(r"[^\w\sáéíóöőúüűàèìòùäëïöüçñßæœ]+", '', s)
        # collapse spaces
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    with app.app_context():
        # gather all events and group by normalized title
        all_events = db.session.query(Event).order_by(Event.created_at.asc()).all()
        groups = {}
        for ev in all_events:
            key = normalize_title(ev.title)
            groups.setdefault(key, []).append(ev)

        total_deleted = 0
        total_res_deleted = 0
        for key, events in groups.items():
            if len(events) <= 1:
                continue
            # work on this group
            events = sorted(events, key=lambda e: e.created_at or e.id)
            if len(events) <= 1:
                continue
            # prefer those with description
            with_desc = [e for e in events if e.description and e.description.strip()]
            to_delete = []
            if with_desc:
                # delete those without description
                to_delete = [e for e in events if not (e.description and e.description.strip())]
            else:
                # none have description, keep earliest, delete others
                to_delete = events[1:]

            # if none selected to_delete but more than 1 with_desc (multiple with description), keep earliest with description
            if not to_delete and len(with_desc) > 1:
                keeper = with_desc[0]
                to_delete = [e for e in with_desc if e.id != keeper.id]

            # if still none selected to_delete but multiple with description, keep earliest with description
            if not to_delete and len(with_desc) > 1:
                keeper = with_desc[0]
                to_delete = [e for e in with_desc if e.id != keeper.id]

            # delete reservations for to_delete events
            for ev in to_delete:
                res_q = db.session.query(Reservation).filter_by(event_id=ev.id)
                res_count = res_q.count()
                if res_count:
                    res_q.delete(synchronize_session=False)
                    total_res_deleted += res_count
                try:
                    db.session.delete(ev)
                    total_deleted += 1
                    print(f'Deleted event id={ev.id} title="{ev.title}"')
                except Exception as ex:
                    db.session.rollback()
                    print('Error deleting event', ev.id, ex)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Commit error:', e)
        print('\nSummary:')
        print('  Events deleted:', total_deleted)
        print('  Reservations deleted:', total_res_deleted)


if __name__ == '__main__':
    run()
