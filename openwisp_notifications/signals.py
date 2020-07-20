from django.dispatch import Signal

notify = Signal(
    providing_args=[  # pylint: disable=invalid-name
        'recipient',
        'actor',
        'verb',
        'action_object',
        'target',
        'description',
        'timestamp',
        'level',
        'data',
    ]
)

notification_type_registered = Signal(providing_args=['notification_type'])
notification_type_unregistered = Signal(providing_args=['notification_type'])
