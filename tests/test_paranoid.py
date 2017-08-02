import unittest

from flask import Flask
from flask_paranoid import Paranoid


class ParanoidTests(unittest.TestCase):
    def _delete_cookie(self, name):
        return (name + '=; Expires=Thu, 01-Jan-1970 00:00:00 GMT; '
                'Max-Age=0; Path=/')

    def test_401(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'foo'
        Paranoid(app)

        @app.route('/')
        def index():
            return 'foobar'

        client = app.test_client(use_cookies=True)

        rv = client.get('/', headers={'User-Agent': 'foo'})
        self.assertEqual(rv.status_code, 200)

        rv = client.get('/', headers={'User-Agent': 'foo'})
        self.assertEqual(rv.status_code, 200)

        rv = client.get('/', headers={'User-Agent': 'bar'})
        self.assertEqual(rv.status_code, 401)
        self.assertIn(self._delete_cookie('session'),
                      rv.headers.getlist('Set-Cookie'))
        self.assertNotIn(self._delete_cookie('remember_token'),
                         rv.headers.getlist('Set-Cookie'))

    def test_redirect_no_domain(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'foo'
        paranoid = Paranoid(app)
        paranoid.redirect_view = '/foobarbaz'

        @app.route('/')
        def index():
            return 'foobar'

        client = app.test_client(use_cookies=True)

        self.assertEqual(paranoid.redirect_view, '/foobarbaz')

        rv = client.get('/', headers={'User-Agent': 'foo'})
        self.assertEqual(rv.status_code, 200)

        rv = client.get('/', headers={'User-Agent': 'bar'})
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.headers['Location'], 'http://localhost/foobarbaz')
        self.assertIn(self._delete_cookie('session'),
                      rv.headers.getlist('Set-Cookie'))
        self.assertNotIn(self._delete_cookie('remember_token'),
                         rv.headers.getlist('Set-Cookie'))

    def test_redirect_domain(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'foo'
        paranoid = Paranoid(app)
        paranoid.redirect_view = 'https://foo.com/foobarbaz'

        @app.route('/')
        def index():
            return 'foobar'

        client = app.test_client(use_cookies=True)

        self.assertEqual(paranoid.redirect_view, 'https://foo.com/foobarbaz')

        rv = client.get('/', headers={'User-Agent': 'foo'})
        self.assertEqual(rv.status_code, 200)

        rv = client.get('/', headers={'User-Agent': 'bar'})
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.headers['Location'], 'https://foo.com/foobarbaz')
        self.assertIn(self._delete_cookie('session'),
                      rv.headers.getlist('Set-Cookie'))
        self.assertNotIn(self._delete_cookie('remember_token'),
                         rv.headers.getlist('Set-Cookie'))

    def test_redirect_view(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'foo'
        paranoid = Paranoid(app)
        paranoid.redirect_view = 'custom_redirect'

        @app.route('/')
        def index():
            return 'foobar'

        @app.route('/redirect')
        def custom_redirect():
            return 'foo'

        client = app.test_client(use_cookies=True)

        self.assertEqual(paranoid.redirect_view, 'custom_redirect')

        rv = client.get('/', headers={'User-Agent': 'foo'})
        self.assertEqual(rv.status_code, 200)

        rv = client.get('/', headers={'User-Agent': 'bar'})
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.headers['Location'], 'http://localhost/redirect')
        self.assertIn(self._delete_cookie('session'),
                      rv.headers.getlist('Set-Cookie'))
        self.assertNotIn(self._delete_cookie('remember_token'),
                         rv.headers.getlist('Set-Cookie'))

    def test_callback(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'foo'
        paranoid = Paranoid()
        paranoid.init_app(app)
        paranoid.redirect_view = 'custom_redirect'

        @app.route('/')
        def index():
            return 'foobar'

        @paranoid.on_invalid_session
        def custom_callback():
            return 'foo'

        client = app.test_client(use_cookies=True)

        self.assertEqual(paranoid.redirect_view, custom_callback)

        rv = client.get('/', headers={'User-Agent': 'foo'})
        self.assertEqual(rv.status_code, 200)

        rv = client.get('/', headers={'User-Agent': 'bar'})
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.get_data(as_text=True), 'foo')
        self.assertIn(self._delete_cookie('session'),
                      rv.headers.getlist('Set-Cookie'))
        self.assertNotIn(self._delete_cookie('remember_token'),
                         rv.headers.getlist('Set-Cookie'))

    def test_flask_login(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'foo'
        paranoid = Paranoid(app)
        paranoid.redirect_view = 'https://foo.com/foobarbaz'

        @app.route('/')
        def index():
            return 'foobar'

        client = app.test_client(use_cookies=True)
        app.login_manager = 'foo'

        self.assertEqual(paranoid.redirect_view, 'https://foo.com/foobarbaz')

        rv = client.get('/', headers={'User-Agent': 'foo'})
        self.assertEqual(rv.status_code, 200)

        rv = client.get('/', headers={'User-Agent': 'bar'})
        delattr(app, 'login_manager')
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.headers['Location'], 'https://foo.com/foobarbaz')
        self.assertIn(self._delete_cookie('session'),
                      rv.headers.getlist('Set-Cookie'))
        self.assertIn(self._delete_cookie('remember_token'),
                      rv.headers.getlist('Set-Cookie'))
