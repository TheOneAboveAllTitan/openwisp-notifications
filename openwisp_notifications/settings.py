from django.conf import settings
from notifications.settings import CONFIG_DEFAULTS

CONFIG_DEFAULTS.update({'USE_JSONFIELD': True})

OPENWISP_NOTITIFCATION_EMAIL_TEMPLATE = getattr(
    settings,
    'OPENWISP_NOTITIFCATION_EMAIL_TEMPLATE',
    'openwisp_notifications/email_template.html',
)

OPENWISP_NOTIFICATION_EMAIL_LOGO = getattr(
    settings, 'OPENWISP_NOTIFICATION_EMAIL_LOGO', 'https://git.io/JfVhe'
)


def get_config():
    user_config = getattr(settings, 'OPENWISP_NOTIFICATIONS_CONFIG', {})
    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)
    return config
