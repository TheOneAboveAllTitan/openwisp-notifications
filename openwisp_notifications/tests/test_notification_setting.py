from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from openwisp_notifications.handlers import (
    notification_type_registered_unregistered_handler,
)
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.tests.test_helpers import (
    base_register_notification_type,
    base_unregister_notification_type,
    register_notification_type,
    unregister_notification_type,
)
from openwisp_notifications.types import get_notification_configuration
from openwisp_users.tests.utils import TestOrganizationMixin

test_notification_type = {
    'verbose_name': 'Test Notification Type',
    'level': 'test',
    'verb': 'testing',
    'message': '{notification.verb} initiated by {notification.actor} since {notification}',
    'email_subject': '[{site.name}] {notification.verb} reported by {notification.actor}',
}

NotificationSetting = load_model('NotificationSetting')
Organization = swapper_load_model('openwisp_users', 'Organization')
OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')

ns_queryset = NotificationSetting.objects.filter(type='default')


class TestNotificationSetting(TestOrganizationMixin, TestCase):
    def tearDown(self):
        super().tearDown()
        try:
            unregister_notification_type('test')
        except ImproperlyConfigured:
            pass

    def test_no_user(self):
        self.assertEqual(ns_queryset.count(), 0)

    def test_superuser_created(self):
        admin = self._get_admin()
        # One global notification setting and one for default notification
        self.assertEqual(ns_queryset.filter(user=admin).count(), 2)

    def test_user_created(self):
        user = self._get_user()

        self.assertEqual(ns_queryset.count(), 1)
        notification_setting = ns_queryset.first()
        self.assertEqual(notification_setting.user, user)
        self.assertEqual(notification_setting.type, 'default')
        self.assertEqual(notification_setting.organization, None)

    def test_notification_type_registered_unregistered(self):
        register_notification_type('test', test_notification_type)
        queryset = NotificationSetting.objects.filter(type='test')

        self._get_user()
        self.assertEqual(queryset.count(), 1)

        self._get_admin()
        self.assertEqual(queryset.count(), 3)

    def test_organization_created_no_initial_user(self):
        org = self._get_org()
        queryset = ns_queryset.filter(organization=org)
        self.assertEqual(ns_queryset.count(), 0)

        # Notification setting is not created for normal user
        self._get_user()
        self.assertEqual(queryset.count(), 0)

        self._get_admin()
        self.assertEqual(queryset.count(), 1)

    def test_organization_user(self):
        user = self._get_user()
        org = self._get_org()
        org_user = OrganizationUser.objects.create(user=user, organization=org)
        self.assertEqual(ns_queryset.count(), 2)

        org_user.delete()
        # Global notification setting for 'default' type is not deleted.
        self.assertEqual(ns_queryset.count(), 1)

    def test_register_notification_org_user(self):
        self._get_org_user()

        queryset = NotificationSetting.objects.filter(type='test')
        self.assertEqual(queryset.count(), 0)
        register_notification_type('test', test_notification_type)
        self.assertEqual(queryset.count(), 2)

    def test_post_migration_handler(self):
        # Simulates loading of app when Django server starts
        admin = self._get_admin()
        org_user = self._get_org_user()
        self.assertEqual(ns_queryset.count(), 5)

        default_type_config = get_notification_configuration('default')
        base_unregister_notification_type('default')
        base_register_notification_type('test', test_notification_type)
        notification_type_registered_unregistered_handler(sender=self)

        # Notification Setting for "default" type are deleted
        self.assertEqual(ns_queryset.count(), 0)

        # Notification Settings for "test" type are created
        queryset = NotificationSetting.objects
        if NotificationSetting._meta.app_label == 'sample_notifications':
            self.assertEqual(queryset.count(), 10)
            self.assertEqual(queryset.filter(user=admin).count(), 6)
            self.assertEqual(queryset.filter(user=org_user.user).count(), 4)
        else:
            self.assertEqual(queryset.count(), 5)
            self.assertEqual(queryset.filter(user=admin).count(), 3)
            self.assertEqual(queryset.filter(user=org_user.user).count(), 2)

        base_register_notification_type('default', default_type_config)

    def test_superuser_demoted_to_user(self):
        admin = self._get_admin()
        admin.is_superuser = False
        admin.save()

        self.assertEqual(ns_queryset.count(), 1)
        notification_setting = ns_queryset.first()
        self.assertEqual(notification_setting.organization, None)

    def test_superuser_demoted_to_org_user(self):
        admin = self._get_admin()
        admin.is_superuser = False
        admin.save()
        org = Organization.objects.get(name='default')
        OrganizationUser.objects.create(user=admin, organization=org)

        self.assertEqual(ns_queryset.count(), 2)
        self.assertIsNone(ns_queryset.first().organization)
        self.assertEqual(ns_queryset.last().organization, org)

    def test_notification_setting_full_clean(self):
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': 'Test message',
            'email_subject': 'Test Email Subject',
            'web_notification': False,
            'email_notification': False,
        }
        register_notification_type('test_type', test_type)
        self._get_admin()
        queryset = NotificationSetting.objects.filter(type='test_type')
        queryset.update(email=False, web=False)
        notification_setting = queryset.first()

        notification_setting.full_clean()
        self.assertIsNone(notification_setting.email)
        self.assertIsNone(notification_setting.web)

        unregister_notification_type('test_type')
