# Copyright 2014-2018 'ACSONE SA/NV'
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo import fields, models

from .. import utils

_logger = logging.getLogger(__name__)
_logger.info("Loading user model extension")

class Users(models.Model):
    _inherit = "res.users"
    sso_user = fields.Char("SSO User", readonly=True, copy=False) 
    sso_session = fields.Char("SSO Session", readonly=True, copy=False) 

    def _check_credentials(self, password, env=None):
        _logger.info(f"_check_credentials() is searching for {password}")
        res = self.sudo().search([("id", "=", self._uid), ("sso_session", "=", password)])

        if res:
            _logger.info("User authenticated via SSO")
        else:
            _logger.info("_check_credentials() did not find what it was looking for, delegating to default ODOO authentication")
            return super()._check_credentials(password, env)
