from hashlib import sha256

from flask import session, request, make_response, url_for, current_app, \
    redirect
from werkzeug.exceptions import Unauthorized


class Paranoid(object):
    def __init__(self, app=None):
        self.invalid_session_handler = self._default_invalid_session_handler
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        @app.before_request
        def before_request():
            token = self.create_token()
            existing_token = self.get_token_from_session()
            if existing_token is None:
                # this is a new session, so we write our id in it
                self.write_token_to_session(token)
            elif existing_token != token:
                # this session is invalid, so we get rid of it
                response = make_response(self.invalid_session_handler())
                self.clear_session(response)
                return response

    def on_invalid_session(self, f):
        self.invalid_session_handler = f
        return f

    def _default_invalid_session_handler(self):
        try:
            raise Unauthorized()
        except Exception as e:
            response = current_app.handle_user_exception(e)
        return response

    @property
    def redirect_view(self):
        return self.on_invalid_session
    
    @redirect_view.setter
    def redirect_view(self, view):
        @self.on_invalid_session
        def _redirect():
            if view.startswith(('http://', 'https://', '/')):
                url = view
            else:
                url = url_for(view)
            return redirect(url)

    def _get_remote_addr(self):
        address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if address is not None:
            address = address.encode('utf-8').split(b',')[0].strip()
        return address

    def create_token(self):
        """Create a session protection token for this client.
        
        This method generates a session protection token for the cilent, which
        consists in a hash of the user agent and the IP address. This method
        can be overriden by subclasses to implement different token generation
        algorithms.
        """
        user_agent = request.headers.get('User-Agent')
        if user_agent is not None:
            user_agent = user_agent.encode('utf-8')
        base = self._get_remote_addr() + b'|' + user_agent
        h = sha256()
        h.update(base)
        return h.hexdigest()
    
    def get_token_from_session(self):
        """Return the session protection token stored from the client session.

        This method retrieves the stored session protection token, or None if
        this is a brand new session that doesn't have a token in it. This
        default implementation finds the token in the user session. Subclasses
        can override this method and implement other storage methods.
        """
        return session.get('_paranoid_token')
    
    def write_token_to_session(self, token):
        """Write a session protection token to the client session.

        This methods writes the session protection token. This default
        implementation writes the token to the user session. Subclasses can
        override this method to implement other storage methods.
        """
        session['_paranoid_token'] = token

    def clear_session(self, response):
        """Clear the session.

        This method is invoked when the session is found to be invalid.
        Subclasses can override this method to implement a custom session
        reset.
        """
        session.clear()

        # if flask-login is installed, we try to clear the
        # "remember me" cookie, just in case it is set
        try:
            import flask_login
        except ImportError:
            pass
        else:
            remember_cookie = current_app.config.get('REMEMBER_COOKIE',
                                                     'remember_token')
            response.set_cookie(remember_cookie, '', expires=0)
