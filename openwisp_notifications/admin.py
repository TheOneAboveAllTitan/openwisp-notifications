from django.contrib import admin

from openwisp_notifications.base.admin import NotificationSettingAdminMixin
from openwisp_notifications.settings import OW_OBJECT_NOTIFICATION_WIDGET
from openwisp_notifications.swapper import load_model
from openwisp_users.admin import UserAdmin
from openwisp_utils.admin import AlwaysHasChangedMixin
from pydoc import locate

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')


class NotificationSettingInline(
    NotificationSettingAdminMixin, AlwaysHasChangedMixin, admin.TabularInline
):
    model = NotificationSetting
    extra = 0

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user == obj


UserAdmin.inlines = [NotificationSettingInline] + UserAdmin.inlines



class Media:
    extend = True
    js = [
        'admin/js/jquery.init.js',
        'openwisp-notifications/js/object-notifications.js',
    ]
    css = {'screen': ['openwisp-notifications/css/object-notifications.css']}


for model_admin_path in OW_OBJECT_NOTIFICATION_WIDGET:
    model_admin = locate(model_admin_path)
    model_admin.Media = Media
