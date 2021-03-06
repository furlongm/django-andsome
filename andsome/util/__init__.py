# Copyright 2010 VPAC
#
# This file is part of django-andsom.
#
# django-andsome is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-andsome is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-andsome  If not, see <http://www.gnu.org/licenses/>.


from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

import datetime

from andsome.middleware.threadlocals import get_current_user


def log_and_message(obj, flag, custom_message=None):

    user = get_current_user()
    opts = obj.__class__._meta

    if not custom_message:

        if flag == ADDITION:
            message = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        elif flag == CHANGE:
            message = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        elif flag == DELETION:
            message=_('The %(name)s "%(obj)s" was deleted successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}

    else:
        message = custom_message

    LogEntry.objects.log_action(
        user.id,
        ContentType.objects.get_for_model(obj.__class__).id,
        obj._get_pk_val(),
        force_unicode(obj),
        flag,
        change_message=message,
        )

    user.message_set.create(message=message)


def unique(seq):
    """Makes a list unique"""
    # Not order preserving
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()



def get_date_range(request, default_start=(datetime.date.today()-datetime.timedelta(days=90)), default_end=datetime.date.today()):

    today = datetime.date.today()

    if request.REQUEST.has_key('start'):
        try:
            years, months, days = request.GET['start'].split('-')
            start = datetime.datetime(int(years), int(months), int(days))
            start = start.date()
        except:
            start = today - datetime.timedelta(days=90)
    else:
        start = default_start

    if request.REQUEST.has_key('end'):
        try:
            years, months, days = request.GET['end'].split('-')
            end = datetime.datetime(int(years), int(months), int(days))
            end = end.date()
        except:
            end = today
    else:
        end = default_end

    return start, end


def is_password_strong(password, old_password=None):
    """Return True if password valid"""
    try:
        from crack import VeryFascistCheck
    except ImportError:
        def VeryFascistCheck(password, old=None):
            if old and password == old:
                return False
            elif len(password) < 6:
                return False
            return True
    try:
        VeryFascistCheck(password, old=old_password)
    except:
	return False

    return True
