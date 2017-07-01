import unittest
from flask import Flask
from flask_paranoid import Paranoid


class ParanoidTests(unittest.TestCase):
    def test_simple(self):
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
