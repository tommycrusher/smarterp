# -*- coding: utf-8 -*-

import logging

import smarterp.release
import smarterp.tools
from smarterp.exceptions import AccessDenied
from smarterp.modules.registry import Registry
from smarterp.tools.translate import _

_logger = logging.getLogger(__name__)

RPC_VERSION_1 = {
        'server_version': smarterp.release.version,
        'server_version_info': smarterp.release.version_info,
        'server_serie': smarterp.release.serie,
        'protocol_version': 1,
}

def exp_login(db, login, password):
    return exp_authenticate(db, login, password, None)

def exp_authenticate(db, login, password, user_agent_env):
    if not user_agent_env:
        user_agent_env = {}
    res_users = Registry(db)['res.users']
    try:
        credential = {'login': login, 'password': password, 'type': 'password'}
        return res_users.authenticate(db, credential, {**user_agent_env, 'interactive': False})['uid']
    except AccessDenied:
        return False

def exp_version():
    return RPC_VERSION_1

def exp_about(extended=False):
    """Return information about the OpenERP Server.

    @param extended: if True then return version info
    @return string if extended is False else tuple
    """

    info = _('See http://openerp.com')

    if extended:
        return info, smarterp.release.version
    return info

def exp_set_loglevel(loglevel, logger=None):
    # TODO Previously, the level was set on the now deprecated
    # `smarterp.netsvc.Logger` class.
    return True

def dispatch(method, params):
    g = globals()
    exp_method_name = 'exp_' + method
    if exp_method_name in g:
        return g[exp_method_name](*params)
    else:
        raise Exception("Method not found: %s" % method)
