from django.conf import settings
from django.core import checks

from openwisp_notifications import settings as app_settings


@checks.register
def check_cors_configuration(app_configs, **kwargs):
    errors = []
    if not app_settings.OPENWISP_NOTIFICATIONS_HOST:
        return errors

    if not (
        'corsheaders' in settings.INSTALLED_APPS
        and 'corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE
    ):
        errors.append(
            checks.Warning(
                msg='Improperly Configured',
                hint=(
                    '"django-cors-headers" is either not installed or improperly configured.'
                    ' CORS configuration is required for using "OPENWISP_NOTIFICATIONS_HOST" settings.'
                    ' Configure equivalent CORS rules on your server if you are not using'
                    ' "django-cors-headers".'
                ),
                obj='Settings',
            )
        )
    return errors


@checks.register
def check_ow_object_notification_widget_setting(app_configs, **kwargs):
    errors = []
    if not isinstance(app_settings.OW_OBJECT_NOTIFICATION_WIDGET, list):
        errors.append(
            checks.Warning(
                msg='Improperly Configured',
                hint=(
                    'OW_OBJECT_NOTIFICATION_WIDGET should be a list,'
                    f' {type(app_settings.OW_OBJECT_NOTIFICATION_WIDGET)} provided'
                ),
                obj='Settings',
            )
        )
    for model_admin in app_settings.OW_OBJECT_NOTIFICATION_WIDGET:
        if not isinstance(model_admin, str):
            errors.append(
                checks.Error(
                    msg='Improperly Configured',
                    hint=(
                        'OW_OBJECT_NOTIFICATION_WIDGET should contain dotted path string'
                        f'to ModelAdmin, found {type(app_settings.OW_OBJECT_NOTIFICATION_WIDGET)}'
                    ),
                    obj='Settings',
                )
            )
    return errors
