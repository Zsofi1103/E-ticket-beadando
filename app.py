from os import environ
from WebApp import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    # Enable debug by default (can be overridden by env var)
    debug_env = environ.get('FLASK_ENV') == 'development' or environ.get('DEBUG') == '1' or environ.get('FLASK_DEBUG') == '1' or True
    app.run(host=HOST, port=PORT, debug=debug_env)