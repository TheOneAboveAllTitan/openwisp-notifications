from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model
from openwisp_users.tests.utils import TestOrganizationMixin

ObjectNotification = load_model('ObjectNotification')
Notification = load_model('Notification')
on_queryset = ObjectNotification.objects


class TestObjectNotification(TestOrganizationMixin, TestCase):
    def setUp(self):
        self.obj = self._get_org_user()
        self.admin = self._get_admin()

    def test_object_notification(self):
        ObjectNotification.objects.create(
            object=self.obj, user=self.admin, valid_till=timezone.now()
        )
        # Celery task deletes it right away
        self.assertEqual(on_queryset.count(), 0)

    @patch('openwisp_notifications.tasks.delete_objectnotification_object.apply_async')
    def test_delete_object_busy_worker(self, mocked_task):
        ObjectNotification.objects.create(
            object=self.obj, user=self.admin, valid_till=timezone.now()
        )
        self.assertEqual(on_queryset.count(), 1)

    @patch('openwisp_notifications.tasks.delete_objectnotification_object.apply_async')
    def test_notification_for_disabled_object(self, mocked_task):
        ObjectNotification.objects.create(
            object=self.obj,
            user=self.admin,
            valid_till=(timezone.now() + timezone.timedelta(days=1)),
        )
        notify.send(sender=self.admin, type='default', target=self.obj)
        self.assertEqual(Notification.objects.count(), 0)
