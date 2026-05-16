from WebApp import app, db
from WebApp.managers.eventmanager import EventManager
from flask import render_template

def run(event_id=None):
    em = EventManager(db)
    with app.test_request_context('/'):
        if event_id is None:
            # pick a recent event
            from WebApp.models.event import Event
            ev = db.session.query(Event).order_by(Event.created_at.desc()).first()
            event_id = ev.id if ev else None
        event = em.get_event(event_id)
        html = render_template('event/detail.html', event=event, reservation_form=None)
        print('Rendered detail for event id=', event_id)
        # print a small snippet around the category row
        start = html.find('<th>Kategória')
        if start!=-1:
            snippet = html[start: start+300]
            print(snippet)
        else:
            print('No category row found in rendered HTML')

if __name__ == '__main__':
    run()
