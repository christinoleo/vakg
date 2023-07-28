import os

import dash_auth


def setup_auth(app):
    if not os.getenv('DEBUG', False):
        VALID_USERNAME_PASSWORD_PAIRS = {
            'asdasd': 'asdasdasdasd',
        }
        auth = dash_auth.BasicAuth(
            app,
            VALID_USERNAME_PASSWORD_PAIRS
        )
        return auth
