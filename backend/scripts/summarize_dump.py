import json
p = 'eticket_dump_before_restore.json'
with open(p, encoding='utf-8') as f:
    j = json.load(f)
print('SUMMARY of', p)
print('users:', len(j.get('users', [])))
print('events:', len(j.get('events', [])))
print('categories:', len(j.get('categories', [])))
print('event_categories:', len(j.get('event_categories', [])))
print('reservations:', len(j.get('reservations', [])))
