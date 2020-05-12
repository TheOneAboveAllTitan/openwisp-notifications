from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class OpenwispNotificationsConfig(AppConfig):
    name = 'openwisp_notifications'
    verbose_name = _('Openwisp Notifications')

    def ready(self):
        from openwisp_notifications.signals import notify
        from openwisp_notifications.handlers import notify_handler

        notify.connect(
            notify_handler, dispatch_uid='openwisp_notifications.model.notifications'
        )
        self.add_default_menu_items()

    def add_default_menu_items(self):
        menu_setting = 'OPENWISP_DEFAULT_ADMIN_MENU_ITEMS'
        items = [{'model': 'openwisp_notifications.Notification'}]
        if not hasattr(settings, menu_setting):
            setattr(settings, menu_setting, items)
        else:
            current_menu = getattr(settings, menu_setting)
            current_menu += items
