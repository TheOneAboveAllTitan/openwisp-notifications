from django.core.exceptions import ImproperlyConfigured
from openwisp_notifications.settings import ADDITIONAL_NOTIFICATION_TYPES

DEFAULT_NOTIFICATION_TYPES = {
    'default': {'level': 'info', 'verb': 'default verb', 'name': 'Default Type'},
}


def deep_merge_dicts(dict1, dict2):
    result = dict1.copy()
    for key, value in dict2.items():
        if isinstance(value, dict):
            node = result.get(key, {})
            result[key] = deep_merge_dicts(node, value)
        else:
            result[key] = value
    return result


def get_notification_types():
    notification_types = deep_merge_dicts(
        DEFAULT_NOTIFICATION_TYPES, ADDITIONAL_NOTIFICATION_TYPES
    )
    validate_notification_type(notification_types)
    return notification_types


def get_notification_types_choices():
    notification_types = NOTIFICATION_TYPES
    choices = []
    for key in sorted(notification_types.keys()):
        name = notification_types[key].get('name', key)
        choices.append((key, name))
    return choices


def validate_notification_type(notification_type):
    for key, options in notification_type.items():
        assert 'level' in options
        assert 'verb' in options


def register_notification_type(notification_type):
    validate_notification_type(notification_type)
    NOTIFICATION_TYPES.update(notification_type)


def unregister_notifcation_type(notification_type):
    try:
        NOTIFICATION_TYPES.pop(notification_type)
    except KeyError:
        raise ImproperlyConfigured(f'No such Notification Type, {notification_type}')


NOTIFICATION_TYPES = get_notification_types()
