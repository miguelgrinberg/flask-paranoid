flask-paranoid
==============

[![tests](https://code.miguelgrinberg.com/miguelgrinberg/flask-paranoid/badges/workflows/tests.yml/badge.svg)](https://code.miguelgrinberg.com/miguelgrinberg/flask-paranoid/actions)

Simple user session protection.

Quick Start
-----------

Here is a simple application that uses Flask-Paranoid to protect the user session:

```python
from flask import Flask
from flask_paranoid import Paranoid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

paranoid = Paranoid(app)
paranoid.redirect_view = '/'

@app.route('/')
def index():
    return render_template('index.html')
```

When a client connects to this application, a "paranoid" token will be
generated according to the IP address and user agent. In all subsequent
requests, the token will be recalculated and checked against the one computed
for the first request. If the session cookie is stolen and the attacker tries
to use it from another location, the generated token will be different, and in
that case the extension will clear the session and block the request.

Resources
---------

- [git](https://code.miguelgrinberg.com/miguelgrinberg/flask-paranoid)
- [Change Log](https://code.miguelgrinberg.com/miguelgrinberg/flask-paranoid/src/branch/main/CHANGES.md)
- [Documentation](https://flask-paranoid.readthedocs.io/)
- [PyPI](https://pypi.python.org/pypi/flask-paranoid)
- [Contributor's guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

Sponsor this project
--------------------

This project relies on contributions from its users. If you benefit from it please consider making a single or ongoing monetary contribution in one of the following platforms:

- [Github Sponsors](https://github.com/sponsors/miguelgrinberg)
- [Patreon](https://patreon.com/miguelgrinberg)
- [Buy me a Coffee](https://buymeacoffee.com/miguelgrinberg)
- [thanks.dev](https://thanks.dev/u/gh/miguelgrinberg)
- [PayPal](https://paypal.me/miguelgrinberg)

Thank you!
