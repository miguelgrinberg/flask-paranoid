flask-paranoid
==============

[![Build status](https://github.com/miguelgrinberg/flask-paranoid/workflows/build/badge.svg)](https://github.com/miguelgrinberg/flask-paranoid/actions) [![codecov](https://codecov.io/gh/miguelgrinberg/flask-paranoid/branch/main/graph/badge.svg)](https://codecov.io/gh/miguelgrinberg/flask-paranoid)

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

- [Documentation](http://pythonhosted.org/Flask-Paranoid)
- [PyPI](https://pypi.python.org/pypi/flask-paranoid)
