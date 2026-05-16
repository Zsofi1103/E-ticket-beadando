from WebApp import app

with app.test_client() as client:
    resp = client.get('/')
    print('STATUS:', resp.status_code)
    print(resp.get_data(as_text=True))
