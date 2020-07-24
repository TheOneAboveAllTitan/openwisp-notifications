from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.types import NOTIFICATION_TYPES

User = get_user_model()

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')

Organization = swapper_load_model('openwisp_users', 'Organization')
OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')


@shared_task
def delete_obsolete_notifications(instance_app_label, instance_model, instance_id):
    """
    Delete notifications having 'instance' as actor, action or target object.
    """
    instance_content_type = ContentType.objects.get_by_natural_key(
        instance_app_label, instance_model
    )
    where = (
        Q(actor_content_type=instance_content_type)
        | Q(action_object_content_type=instance_content_type)
        | Q(target_content_type=instance_content_type)
    )
    where = where & (
        Q(actor_object_id=instance_id)
        | Q(action_object_object_id=instance_id)
        | Q(target_object_id=instance_id)
    )
    Notification.objects.filter(where).delete()


@shared_task
def delete_notification(notification_id):
    Notification.objects.filter(pk=notification_id).delete()


# Following tasks updates notification settings in database.
# 'ns' is short for notification_setting
@shared_task
def ns_user_created(instance_id, is_superuser, is_created):
    """
    Adds notification setting for all notification types
    and organizations.
    """

    # When a user is demoted from superuser status,
    # only keep notification settings for organisation they are member of.
    if not (is_superuser or is_created):
        orgs_membership = OrganizationUser.objects.filter(user_id=instance_id).values(
            'organization'
        )
        NotificationSetting.objects.filter(user_id=instance_id).exclude(
            Q(organization__in=orgs_membership) | Q(organization=None)
        ).delete()
        return

    notification_types = NOTIFICATION_TYPES.keys()
    notification_settings = []
    for type in notification_types:
        if is_superuser:
            for org in Organization.objects.iterator():
                notification_settings.append(
                    NotificationSetting(
                        user_id=instance_id, type=type, organization=org
                    )
                )

        NotificationSetting.objects.get_or_create(
            user_id=instance_id, type=type, organization=None,
        )

    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )


@shared_task
def ns_register_unregister_notification_type(
    notification_type=None, delete_unregistered=True
):
    """
    Creates notification setting for registeterd notification types.
    Deletes notification for unregistered notification types.
    """

    notification_types = (
        [notification_type] if notification_type else NOTIFICATION_TYPES.keys()
    )
    notification_settings = []
    organizations = Organization.objects.all()
    organization_users = OrganizationUser.objects.all()

    for type in notification_types:
        for user in User.objects.filter(is_superuser=True):
            # Superusers receives notifications for all organizations
            # irrespective of their membership.
            for org in organizations:
                notification_settings.append(
                    NotificationSetting(user=user, type=type, organization=org)
                )

            # Add a global notification setting
            NotificationSetting.objects.get_or_create(
                user_id=user.id, type=type, organization=None,
            )

        # OrganizationUsers receives notifications for organization they
        # are member of.
        for org_user in organization_users:
            notification_settings.append(
                NotificationSetting(
                    user_id=org_user.user_id,
                    organization_id=org_user.organization_id,
                    type=type,
                )
            )

        # Add a global notificattion setting for non-superuser
        for user in User.objects.filter(is_superuser=False):
            NotificationSetting.objects.get_or_create(
                user_id=user.id, type=type, organization=None,
            )

    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )

    if delete_unregistered:
        # Delete all notification settings for unregistered notification types
        NotificationSetting.objects.exclude(type__in=notification_types).delete()


@shared_task
def ns_organization_user_added(instance_user_id, instance_org_id):
    """
    Adds notification settings for all notification types when a new
    organization user is added.
    """
    notification_settings = []
    for notification_type in NOTIFICATION_TYPES.keys():
        notification_settings.append(
            NotificationSetting(
                user_id=instance_user_id,
                organization_id=instance_org_id,
                type=notification_type,
            )
        )

    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )


@shared_task
def ns_organization_user_deleted(instance_user_id, instance_org_id):
    """
    Deletes notification settings for all notification types when
    an organization user is deleted.
    """
    NotificationSetting.objects.filter(
        user_id=instance_user_id, organization_id=instance_org_id
    ).delete()


@shared_task
def ns_organization_created(instance_id):
    """
    Adds notification setting of all registered types
    for a newly created organization.
    """
    notification_types = NOTIFICATION_TYPES.keys()
    notification_settings = []
    for user in User.objects.filter(is_superuser=True):
        for type in notification_types:
            notification_settings.append(
                NotificationSetting(
                    user_id=user.id, type=type, organization_id=instance_id
                )
            )
    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )
