#!/usr/bin/env python
"""
Create main categories and import listed events into those categories.
Idempotent: will not duplicate categories or events; will attach category to existing events if missing.

Run from project root: python create_main_categories.py
"""
from WebApp import db, app

mapping = [
    ("Színház, Irodalom, Előadó-művészet", [
        "Poetry Slam",
        "Irodalmi Est",
        "Hamlet – Színházi előadás",
    ]),
    ("Zene és Koncertek", [
        "Adventi Kóruskoncert",
        "Városi Jazz Est",
        "Jazz est a Városligetben",
        "Operett Est",
        "Művészek Éjszakája – Koncert",
    ]),
    ("Kiállítások, Művészet", [
        "Kortárs Művészet Kiállítás",
        "Művészek Éjszakája – Koncert",
        "Fotóséta a Belvárosban",
    ]),
    ("Gasztronómia", [
        "Vegan Brunch Pop-up",
        "Gasztro Workshop",
        "Borfeszt Hétvége",
    ]),
    ("Tech & Innováció", [
        "Robotika Bemutató",
        "Tech Meetup 12",
        "Startup Pitch Night",
    ]),
    ("Sport és Egészség", [
        "Közösségi Futónap",
        "Jóga a Parkban",
    ]),
    ("Közösségi / Szabadidős Programok", [
        "Asztali Játék Est",
        "Közösségi Filmklub",
        "Fotóséta a Belvárosban",
        "Önkéntes Nap",
    ]),
    ("Tudomány & Ismeretterjesztés", [
        "Csillagászati Éjszaka",
    ]),
    ("Ünnepi / Szezonális Programok", [
        "Karácsonyi Vásár",
        "Adventi Kóruskoncert",
    ]),
    ("Népi & Kulturális Hagyományok", [
        "Táncház – Moldvai",
    ]),
]


def run():
    from WebApp.models.category import Category
    from WebApp.models.event import Event

    created_categories = 0
    created_events = 0
    attached = 0

    with app.app_context():
        for cat_name, titles in mapping:
            cat = db.session.scalar(db.select(Category).filter_by(name=cat_name))
            if not cat:
                cat = Category(name=cat_name)
                db.session.add(cat)
                db.session.flush()
                created_categories += 1
                print(f'Created category: {cat_name}')
            else:
                print(f'Category exists: {cat_name}')

            for t in titles:
                # find event by exact title
                ev = db.session.scalar(db.select(Event).filter_by(title=t))
                if not ev:
                    ev = Event(title=t, description='')
                    db.session.add(ev)
                    db.session.flush()
                    created_events += 1
                    print(f'  Created event: {t}')
                else:
                    print(f'  Event exists: {t}')

                # attach category if not already attached
                if not any(c.id == cat.id for c in ev.categories):
                    ev.categories.append(cat)
                    attached += 1
                    print(f'    Attached category "{cat_name}" to event "{t}"')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error committing changes:', e)
            return

    print('\nSummary:')
    print('  Categories created:', created_categories)
    print('  Events created:', created_events)
    print('  Category attachments added:', attached)


if __name__ == '__main__':
    run()
