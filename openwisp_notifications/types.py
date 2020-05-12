from django.core.exceptions import ImproperlyConfigured

NOTIFICATION_TYPES = {
    'default': {
        'level': 'info',
        'verb': 'default verb',
        'name': 'Default Type',
        'email_subject': '[{site}] Default Notification Subject',
        'description': 'Default notification with {opts.verb} and {opts.level}',
    },
}

NOTIFICATION_CHOICES = [('default', 'Default Type')]


def get_notification_configuration(notification_type):
    if not notification_type:
        return {}
    try:
        return NOTIFICATION_TYPES[notification_type]
    except KeyError:
        raise ImproperlyConfigured(f'No such Notification Type, {notification_type}')


def _validate_notification_type(type_config):
    options = type_config.keys()
    assert 'level' in options
    assert 'verb' in options
    assert 'description' in options
    assert 'email_subject' in options


def register_notification_type(type_name, type_config):
    """
    Registers a new notification type.
    register_notification_type(str,dict)
    """
    if not isinstance(type_name, str):
        raise ImproperlyConfigured('Notification Type name should be type `str`.')
    if not isinstance(type_config, dict):
        raise ImproperlyConfigured(
            'Notification Type configuration should be type `dict`.'
        )
    if type_name in NOTIFICATION_TYPES:
        raise ImproperlyConfigured(
            f'{type_name} is an already registered Notification Type.'
        )

    _validate_notification_type(type_config)
    NOTIFICATION_TYPES.update({type_name: type_config})
    _register_notification_choice(type_name, type_config)


def unregister_notification_type(type_name):
    if not isinstance(type_name, str):
        raise ImproperlyConfigured('Notification Type name should be type `str`')
    if type_name not in NOTIFICATION_TYPES:
        raise ImproperlyConfigured(f'No such Notification Type, {type_name}')

    NOTIFICATION_TYPES.pop(type_name)
    _unregister_notification_choice(type_name)


def _register_notification_choice(type_name, type_config):
    name = type_config.get('verbose_name', type_name)
    NOTIFICATION_CHOICES.append((type_name, name))


def _unregister_notification_choice(notification_type):
    for index, (key, name) in enumerate(NOTIFICATION_CHOICES):
        if key == notification_type:
            NOTIFICATION_CHOICES.pop(index)
            return
    raise ImproperlyConfigured(f'No such Notification Choice {notification_type}')
