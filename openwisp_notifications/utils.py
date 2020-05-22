from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html


def _get_object_link(obj, field, html=True):
    content_type = getattr(obj, f'{field}_content_type', None)
    object_id = getattr(obj, f'{field}_object_id', None)
    try:
        url = reverse(
            f'admin:{content_type.app_label}_{content_type.model}_change',
            args=[object_id],
        )
        if not html:
            return url
        return format_html(f'<a href="{url}" id="{field}-object-url">{object_id}</a>')
    except NoReverseMatch:
        return object_id
    except AttributeError:
        return '-'
