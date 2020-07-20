from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OpenwispNotificationsConfig(AppConfig):
    name = 'openwisp_notifications'
    label = 'openwisp_notifications'
    verbose_name = _('Notifications')

    def ready(self):
        from openwisp_notifications.signals import (
            notification_type_registered,
            notification_type_unregistered,
            notify,
        )
        from openwisp_notifications.handlers import (
            notify_handler,
            notification_type_registered_handler,
            notification_type_unregistered_handler,
        )

        notify.connect(
            notify_handler, dispatch_uid='openwisp_notifications.model.notifications'
        )
        notification_type_registered.connect(
            notification_type_registered_handler,
            dispatch_uid='notification_type_registered',
        )
        notification_type_unregistered.connect(
            notification_type_unregistered_handler,
            dispatch_uid='notification_type_unregistered',
        )
        # Add CORS configuration checks
        from openwisp_notifications.checks import check_cors_configuration  # noqa
