# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library
from django.utils.html import format_html
from notifications.templatetags.notifications_tags import (
    notifications_unread as base_notification_unread,
)
from openwisp_notifications.swapper import load_model

Notification = load_model('Notification')

register = Library()


def get_notifications_count(context):
    user_pk = context['user'].is_authenticated and context['user'].pk
    cache_key = Notification.COUNT_CACHE_KEY.format(user_pk)
    count = cache.get(cache_key)
    if count is None:
        count = base_notification_unread(context)
        count = '99+' if count > 99 else count
        cache.set(cache_key, count)
    return count


def unread_notifications(context):
    count = get_notifications_count(context)
    output = ''
    if count:
        output = '<span id="notification-count">{0}</span>'
        output = format_html(output.format(count))
    return output


def notification_widget():
    return format_html(
        '''
        <div class="notification-dropdown hide">
            <div class="filters">
                <span class="btn" id="mark-all-read">Mark all read</span>
                <span class="btn" id="show-unread">Show unread only</span>
            </div>
            <div class="accordion"></div>
            <div class="no-notifications hide">
                <p>No notifications founds.</p>
            </div>
            <div class="loader hide"></div>
        </div>
        '''
    )


def notification_toast():
    return format_html('<div class="toast"></div>')


register.simple_tag(takes_context=True)(unread_notifications)
register.simple_tag(takes_context=False)(notification_widget)
register.simple_tag(takes_context=False)(notification_toast)
