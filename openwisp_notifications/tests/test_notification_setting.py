from django.test import TestCase
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.types import (
    register_notification_type,
    unregister_notification_type,
)

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
    default_org = Organization.objects.get(name='default')

    def test_no_user(self):
        self.assertEqual(ns_queryset.count(), 0)

    def test_superuser_created(self):
        admin = self._get_admin()
        self.assertEqual(ns_queryset.filter(user=admin).count(), 2)

    def test_user_created(self):
        user = self._get_user()

        ns = ns_queryset.first()
        self.assertEqual(ns.user, user)
        self.assertEqual(ns.type, 'default')
        self.assertEqual(ns.organization, None)

    def test_notification_type_registered_unregistered(self):
        register_notification_type('test', test_notification_type)
        self._get_user()

        qs = NotificationSetting.objects.filter(type='test')
        self.assertEqual(qs.count(), 1)

        self._get_admin()
        self.assertEqual(qs.count(), 2)

        # Test unregistering deletes all notification settings
        unregister_notification_type('test')
        self.assertEqual(qs.count(), 0)

    def test_organization_created_no_initial_user(self):
        org = self._get_org()
        qs = ns_queryset.filter(organization=org)
        self.assertEqual(ns_queryset.count(), 0)

        # Notification setting is not created for normal user
        self._get_user()
        self.assertEqual(qs.count(), 0)

        self._get_admin()
        self.assertEqual(qs.count(), 1)

    def test_organization_user(self):
        user = self._get_user()
        org = self._get_org()
        org_user = OrganizationUser.objects.create(user=user, organization=org)
        self.assertEqual(ns_queryset.count(), 2)

        org_user.delete()
        self.assertEqual(ns_queryset.count(), 1)
        # Global notification setting for 'default' type is not deleted.

    def test_register_notification_org_user(self):
        self._get_org_user()
        qs = NotificationSetting.objects.filter(type='test')
        self.assertEqual(qs.count(), 0)

        register_notification_type('test', test_notification_type)
        self.assertEqual(qs.count(), 2)

        unregister_notification_type('test')
