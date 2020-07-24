from openwisp_notifications.base.models import (
    AbstractNotification,
    AbstractNotificationSetting,
)
from swapper import swappable_setting


class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'openwisp_notifications'
        swappable = swappable_setting('openwisp_notifications', 'Notification')


class NotificationSetting(AbstractNotificationSetting):
    class Meta(AbstractNotificationSetting.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_notifications', 'NotificationSetting')
