#
# The Qubes OS Project, https://www.qubes-os.org/
#
# Copyright (C) 2014-2015  Joanna Rutkowska <joanna@invisiblethingslab.com>
# Copyright (C) 2014-2015  Wojtek Porczyk <woju@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

'''Qubes logging routines

See also: :py:attr:`qubes.vm.qubesvm.QubesVM.log`
'''

import logging
import sys

import dbus

FORMAT_CONSOLE = '%(name)s: %(message)s'
FORMAT_LOG = '%(asctime)s %(message)s'
FORMAT_DEBUG = '%(asctime)s ' \
    '[%(processName)s %(module)s.%(funcName)s:%(lineno)d] %(name)s: %(message)s'

formatter_console = logging.Formatter(FORMAT_CONSOLE)
formatter_log = logging.Formatter(FORMAT_LOG)
formatter_debug = logging.Formatter(FORMAT_DEBUG)


class DBusHandler(logging.Handler):
    '''Handler which displays records as DBus notifications'''

    #: mapping of loglevels to icons
    app_icons = {
        logging.ERROR:      'dialog-error',
        logging.WARNING:    'dialog-warning',
        logging.NOTSET:     'dialog-information',
    }

    def __init__(self, *args, **kwargs):
        super(DBusHandler, self).__init__(*args, **kwargs)

        self._notify_object = dbus.SessionBus().get_object(
            'org.freedesktop.Notifications', '/org/freedesktop/Notifications')


    def emit(self, record):
        app_icon = self.app_icons[
            max(level for level in self.app_icons if level <= record.levelno)]

        try:
            # https://developer.gnome.org/notification-spec/#command-notify
            self._notify_object.Notify(
                'Qubes',    # STRING app_name
                0,          # UINT32 replaces_id
                app_icon,   # STRING app_icon
                record.msg, # STRING summary
                '',         # STRING body
                (),         # ARRAY actions
                {},         # DICT hints
                0,          # INT32 timeout
                dbus_interface='org.freedesktop.Notifications')
        except dbus.DBusException:
            pass


def enable():
    '''Enable global logging

    Use :py:mod:`logging` module from standard library to log messages.

    >>> import qubes.log
    >>> qubes.log.enable()          # doctest: +SKIP
    >>> import logging
    >>> logging.warning('Foobar')   # doctest: +SKIP
    '''

    if logging.root.handlers:
        return

    handler_console = logging.StreamHandler(sys.stderr)
    handler_console.setFormatter(formatter_console)
    logging.root.addHandler(handler_console)

    logging.root.setLevel(logging.INFO)


def enable_debug():
    '''Enable debug logging

    Enable more messages and additional info to message format.
    '''

    enable()
    logging.root.setLevel(logging.DEBUG)

    for handler in logging.root.handlers:
        handler.setFormatter(formatter_debug)
