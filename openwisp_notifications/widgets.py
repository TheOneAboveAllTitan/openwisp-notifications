from pydoc import locate

from openwisp_notifications import settings as app_settings


class IgnoreObjectNotificationWidgetMedia:
    extend = True
    js = [
        'admin/js/jquery.init.js',
        'openwisp-notifications/js/object-notifications.js',
    ]
    css = {'all': ['openwisp-notifications/css/object-notifications.css']}


def _add_object_notification_widget():
    """
    Adds object notification widget on configured ModelAdmins.
    """
    for model_admin_path in app_settings.OW_OBJECT_NOTIFICATION_WIDGET:
        model_admin = locate(model_admin_path)
        try:
            if isinstance(model_admin.Media.js, list):
                model_admin.Media.js.extend(IgnoreObjectNotificationWidgetMedia.js)
            elif isinstance(model_admin.Media.js, tuple):
                model_admin.Media.js += tuple(IgnoreObjectNotificationWidgetMedia.js)

            if 'all' in model_admin.Media.css:
                if isinstance(model_admin.Media.css['all'], list):
                    model_admin.Media.css['all'].extend(
                        IgnoreObjectNotificationWidgetMedia.css['all']
                    )
                elif isinstance(model_admin.Media.css['all'], tuple):
                    model_admin.Media.css['all'] += tuple(
                        IgnoreObjectNotificationWidgetMedia.css['all']
                    )
            else:
                model_admin.Media.css.update(IgnoreObjectNotificationWidgetMedia.css)
        except AttributeError:
            model_admin.Media = IgnoreObjectNotificationWidgetMedia
