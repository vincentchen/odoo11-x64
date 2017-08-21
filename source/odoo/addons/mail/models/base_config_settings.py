# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from werkzeug import urls

from odoo import api, fields, models, tools


class BaseConfigSettings(models.TransientModel):
    """ Inherit the base settings to add a counter of failed email + configure
    the alias domain. """
    _inherit = 'base.config.settings'

    fail_counter = fields.Integer('Fail Mail', readonly=True)
    alias_domain = fields.Char('Alias Domain', help="If you have setup a catch-all email domain redirected to "
                               "the Odoo server, enter the domain name here.")

    @api.model
    def get_values(self):
        res = super(BaseConfigSettings, self).get_values()

        previous_date = datetime.datetime.now() - datetime.timedelta(days=30)

        alias_domain = self.env["ir.config_parameter"].get_param("mail.catchall.domain", default=None)
        if alias_domain is None:
            domain = self.env["ir.config_parameter"].get_param("web.base.url")
            try:
                alias_domain = urls.url_parse(domain).host
            except Exception:
                pass

        res.update(
            fail_counter=self.env['mail.mail'].sudo().search_count([
                ('date', '>=', previous_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                ('state', '=', 'exception')]),
            alias_domain=alias_domain or False,
        )

        return res

    def set_values(self):
        super(BaseConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param("mail.catchall.domain", self.alias_domain or '')