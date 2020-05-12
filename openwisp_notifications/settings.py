from django.conf import settings
from notifications.settings import CONFIG_DEFAULTS

CONFIG_DEFAULTS.update({'USE_JSONFIELD': True})


ADDITIONAL_NOTIFICATION_TYPES = getattr(settings, 'OPENWISP_NOTIFICATION_TYPES', {})
MESSAGE_TEMPLATE = getattr(
    settings, 'OPENWISP_NOTIFICATION_MESSAGE_TEMPLATE', 'configurables/message.md'
)


def get_config():
    user_config = getattr(settings, 'OPENWISP_NOTIFICATIONS_CONFIG', {})
    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)
    return config
