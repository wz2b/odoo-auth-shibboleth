# Copyright 2024 Christopher Piggott

# Based on original work done by members of the Odoo Community Association,
# Copyright 2014-2018 'ACSONE SA/NV'
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import werkzeug
from odoo import SUPERUSER_ID, api, http
from odoo.http import request
from odoo.addons.web.controllers.home import Home as HomeBase
from odoo.exceptions import AccessDenied
from .. import utils



_logger = logging.getLogger(__name__)

_logger.info("Loading auth module")

class Home(HomeBase):
    _REMOTE_USER_ATTRIBUTE = "Shib-Mail"
    _REMOTE_SESSION_ATTRIBUTE = "Shib-Shib-Session-Id"

    @http.route("/web", type="http", auth="none")
    def web_client(self, s_action=None, **kw):
        _logger.info("Request parsed")

        try:
            self._bind_http_remote_user(http.request.session.db)
        except Exception:
            return werkzeug.exceptions.Unauthorized().get_response()

        return super().web_client(s_action, **kw)


    #
    # Look at the headers that came in to try to determine who the
    # logged in SSO user is, by his e-mail address.
    # This comes in as two headers.
    #
    def _bind_http_remote_user(self, db_name):
        #
        # Get SSO parameters from HTTP headers
        #
        headers = http.request.httprequest.headers
        sso_user = headers.get(self._REMOTE_USER_ATTRIBUTE, None)
        sso_session = headers.get(self._REMOTE_SESSION_ATTRIBUTE, None)

        # for header, value in headers.items():
        #    _logger.info(f"HEADER {header}: {value}")


        _logger.info(f"SSO user: {sso_user}, session: {sso_session}")

        # 'request' is a proxy object that represents the current request
        # being handled.  It is part of ODOO's HTTP layer and is made
        # available as a global.  Check to see if this is an existing
        # session session for this user.
        current_login = request.session.login

        if (not sso_session) and (not sso_user):
            # No SSO session, so return, which will cause us
            # to fall through to default authentication
            return



        if current_login:
            # There is a current login session
            if current_login == sso_user:
                # This matches the SSO user so there's nothing to do
                return
            else:
                # There is a current login session that matches a
                # different user than the one specified by the
                # SSO, so 
                request.session.logout(keep_db=True)

        #
        # Attempt login
        #
        try:
            _logger.info(f"_bind_http_remote_user() is searching for user '{sso_user}")
            user = request.env["res.users"].sudo().search([('login', '=', sso_user)], limit=1)
            if not user:
                _logger.warning("This user was not found in the database, forcing logout and failing with access denied")
                request.session.logout(keep_db=True)
                raise AccessDenied("user not found")
            
            # Put out a debug message indicating we located this user
            _logger.info(f"_bind_http_remote_user() matched to Odoo user '{user.name}' with login '{user.login}'")

            with request.env.registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {}) 
                user.with_env(env).sudo().write({"sso_user": sso_user, "sso_session": sso_session})

            # Authenticate session without specifying password
            if request.session.authenticate(db_name, sso_user, sso_session):
                _logger.info(f"User {user.login} authenticated via HTTP Remote User")
            else:
                _logger.warning(f"Authentication failed for user {sso_user}")
                raise AccessDenied("Authentication failed")
        except Exception:
            _logger.error("Error binding HTTP remote user", exc_info=True)
            raise
