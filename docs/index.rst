.. flask-paranoid documentation master file, created by
   sphinx-quickstart on Sat Jul  1 17:13:54 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/logo.png
   :alt: flask-paranoid
   :align: center

Flask-Paranoid is a simple extension for the Flask microframework that protects
the application against certain attacks in which the user session cookie is
stolen and then used by the attacker.

How Does It Work?
=================

When a client connects to the application for the first time, a token that
represents certain characteristics of this client is generated and stored. In
succesive requests sent by this client, this token is regenerated and compared
against the stored one. If the tokens are different, it is assumed that the
user session is being used from a different environment than the one in which
the session was originally created, so in this case the session is destroyed
as a preventive measure.

The token that is generated from the IP address and the user agent of the
client. This means that if a user session cookie is stolen and then used from
a different location or from a different browser, the generated token will
change, and that will block this "different" request.

The idea is based on the strong session protection feature of Flask-Login, but
generalized so that it can also be used of the Flask-Login context. The
token generation and storage can be customized to fit different types of
applications.

Quick Start
===========

Here is a simple application that uses Flask-Paranoid to protect the user
session::

    from flask import Flask
    from flask_paranoid import Paranoid

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'top-secret!'

    paranoid = Paranoid(app)
    paranoid.redirect_view = '/'

    @app.route('/')
    def index():
        return render_template('index.html')

In this example, the paranoid token computed on the initial request from a
client will be stored in the user session. If a subsequent request generates
a different token, the session will be cleared and then a redirect to the root
URL will be made, forcing the potential attacker to log in again.

Configuration
=============

The only configuration is what determines the action that is taken when an
invalid session is detected, after the session is cleared. The default is to
return a 401 error back to the client.

To redirect to a given URL, set ``paranoid.redirect_view`` to the desired
location::

    paranoid.redirect_view = '/login'

Absolute URLs are also supported::

    paranoid.redirect_view = 'https://www.google.com'

To redirect to a registered Flask route, set ``paranoid.redirect_view`` to the
desired endpoint name::

    paranoid.redirect_view = 'index'

To redirect to a route inside a blueprint, use the same syntax used by the
``url_for()`` function::

    paranoid.redirect_view = 'auth.login'

To have the extension invoke a callback function that generates the response,
use the ``paranoid.on_invalid_session`` decorator. The function should return
a valid Flask response::

    @paranoid.on_invalid_session
    def invalid_session():
        return 'please login', 401

Using with Flask-Login
======================

Since this extension overrides the similar feature in Flask-Login, it is
recommended that when using both extensions in an application, session
protection is disabled in Flask-Login::

    login_manager.session_protection = None

Flask-Paranoid detects if Flask-Login is being used, and in that case clears
the "remember me" cookie in addition to the user session when an invalid
session is detected.

Customization
=============

Flask-Paranoid allows applications to customize its inner workings through the
use of subclasses.

Changing the Token Generation Algorithm
---------------------------------------

The default implementation creates a SHA256 hash of the client IP address and
user agent.

To use a different token generation algorithm, override the ``create_token``
method::

    class MyParanoid(Paranoid):
        def create_token(self):
            pass

This method is invoked in the context of a request, so it can access the
``request`` object to obtain information about the client.

Changing Where the Token is Stored
----------------------------------

The default implementation writes the paranoid token to
``session['_paranoid_token']``.

If a different storage mechanism is desired, override the
``write_token_to_session()`` and ``get_token_from_session()`` methods::

    class MyParanoid(Paranoid):
        def write_token_to_session(self, token):
            pass

        def get_token_from_session(self):
            pass

A tricky use case is when this extension is used with an API project that
does not use the user session and instead provides authentication tokens to
clients. In such a case, the application's token generation function can be
enhanced to include the paranoid token. For example::

    def get_token(username, password):
        if validate_user(username, password):
            return encode_jwt(claims={'username': username,
                                      'paranoid_token': paranoid.create_token()})

And then the token storage methods can be overriden as follows::

    class MyParanoid(Paranoid):
        def write_token_to_session(self, token):
            # nothing to do here, the paranoid token is inserted in the JWT
            # by the application
            pass

        def get_token_from_session(self):
            claims = decode_jwt(request.headers['X-API-TOKEN'])
            if 'paranoid_token' not in claims:
                abort(401)
            return claims['paranoid_token']

In this example, the ``encode_jwt`` and ``decode_jwt`` are application
functions that work with JWT tokens. The client authenticates by passing the
JWT token in the ``X-API-TOKEN`` header.

Using a Different Session Cleanup Mechanism
-------------------------------------------

By default, this extension empties the contents of the user session, and if
Flask-Login is used, also deletes its "remember me" cookie.

To change or replace the session cleanup algorithm, override the
``clear_session()`` method::

    class MyParanoid(Paranoid):
        def clear_session(self, response):
            pass

The ``response`` argument passed to this method is the response object that
will be returned to the client after the session has been cleaned up. Any
cookies that need to be deleted or modified must be included in this response
object.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
