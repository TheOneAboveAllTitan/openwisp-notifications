# -*- coding: utf-8 -*-
import swapper
from django.core.cache import cache
from django.template import Library
from django.utils.html import format_html
from notifications.templatetags.notifications_tags import notifications_unread

Notification = swapper.load_model('openwisp_notifications', 'Notification')

register = Library()


def get_notifications_count(context):
    user_pk = context['user'].is_authenticated and context['user'].pk
    cache_key = Notification.COUNT_CACHE_KEY.format(user_pk)
    count = cache.get(cache_key)
    if count is None:
        count = notifications_unread(context)
        count = '99+' if count > 99 else count
        cache.set(cache_key, count)
    return count


def unread_notifications(context):
    count = get_notifications_count(context)
    output = ''
    if count:
        output = '<span>{0}</span>'
        output = format_html(output.format(count))
    return output


register.simple_tag(takes_context=True)(unread_notifications)
