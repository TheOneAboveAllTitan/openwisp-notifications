from django.contrib import admin
from openwisp_notifications.base.admin import NotificationSettingAdminMixin
from openwisp_notifications.swapper import load_model

from openwisp_users.admin import UserAdmin
from openwisp_utils.admin import AlwaysHasChangedMixin

Notification = load_model('Notification')
NotificationUser = load_model('NotificationUser')
NotificationSetting = load_model('NotificationSetting')


class NotificationUserInline(AlwaysHasChangedMixin, admin.StackedInline):
    model = NotificationUser
    fields = ['receive', 'email']


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

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            fields = ['user'] + fields
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields.append('user')
        return readonly_fields

    def has_change_permission(self, request, obj=None):
        try:
            user_owns_obj = request.user == obj.user
        except AttributeError:
            user_owns_obj = False
        finally:
            return user_owns_obj or request.user.is_superuser


class NotificationSettingInline(
    NotificationSettingAdminMixin, AlwaysHasChangedMixin, admin.TabularInline
):
    model = NotificationSetting
    extra = 0

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user == obj


UserAdmin.inlines = [NotificationSettingInline] + UserAdmin.inlines
