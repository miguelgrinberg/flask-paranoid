from hashlib import sha256

from flask import session, request


class Paranoid(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        @app.before_request
        def before_request():
            paranoid_id = self.create_identifier()
            if '_paranoid_id' not in session:
                session['_paranoid_id'] = paranoid_id
            elif session['_paranoid_id'] != paranoid_id:
                # this session is invalid, so we get rid of it
                session.clear()

                # if flask-login is installed, we try to clear the
                # "remember me" cookie, just in case it is set
                try:
                    import flask_login
                except ImportError:
                    pass
                else:
                    remember_cookie = app.config.get('REMEMBER_COOKIE',
                                                     'remember_token')
                    request.set_cookie(remember_cookie, '', expires=0)

    def _get_remote_addr(self):
        address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if address is not None:
            address = address.encode('utf-8').split(b',')[0].strip()
        return address

    def create_identifier(self):
        """Create a session identifier for this client which consists in a hash
        of the user agent and the IP address. This method can be overriden by
        a subclass to use a different algorithm.
        """
        user_agent = request.headers.get('User-Agent')
        if user_agent is not None:
            user_agent = user_agent.encode('utf-8')
        base = self._get_remote_addr() + b'|' + user_agent
        h = sha256()
        h.update(base)
        return h.hexdigest()
