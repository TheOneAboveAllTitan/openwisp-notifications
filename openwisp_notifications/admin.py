from django.contrib import admin
from openwisp_notifications.swapper import load_model
from openwisp_notifications.utils import NotificationSettingAdminMixin

from openwisp_users.admin import UserAdmin
from openwisp_utils.admin import AlwaysHasChangedMixin

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')


@admin.register(NotificationSetting)
class NotificationSettingAdmin(
    NotificationSettingAdminMixin, admin.ModelAdmin,
):
    model = NotificationSetting
    list_display = ['type', 'organization']
    list_filter = list_display
    search_fields = ['user__username', 'type', 'organization__name']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user_id=request.user.pk)

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ['user'] + self.list_display
        return self.list_display


class NotificationSettingInline(
    NotificationSettingAdminMixin, AlwaysHasChangedMixin, admin.TabularInline
):
    model = NotificationSetting
    extra = 0


UserAdmin.inlines.insert(len(UserAdmin.inlines) - 1, NotificationSettingInline)
