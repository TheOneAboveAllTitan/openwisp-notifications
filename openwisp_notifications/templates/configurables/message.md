{% block head %} {{ level }} : {{ verb }} {% endblock head %}
{% block body %}
{{ actor }} {{ verb }} {% if target %} for {{ target }}. {% endif %}
{% if url %} For more info, see {{ url }}. {% endif %}
{% endblock body %}
