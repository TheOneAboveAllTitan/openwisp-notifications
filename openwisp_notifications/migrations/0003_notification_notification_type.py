from django.db import migrations, models
from openwisp_notifications.notification_types import get_notification_types_choices


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_notifications', '0002_default_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                choices=get_notification_types_choices(),
                max_length=30,
                null=True,
                verbose_name='Type',
            ),
        ),
    ]
