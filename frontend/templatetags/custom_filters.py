from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns the value from the dictionary using the provided key."""
    return dictionary.get(key)

@register.filter(name='dictvalue')
def dictvalue(d, key):
    return d.get(key)

# frontend/templatetags/time_extras.py

@register.filter
def time_display(minutes):
    """
    Converts an integer minute-of-day (e.g. 540) into HH:MM (e.g. '09:00').
    """
    try:
        hour = int(minutes) // 60
        minute = int(minutes) % 60
        return f"{hour:02d}:{minute:02d}"
    except (ValueError, TypeError):
        return ''


@register.filter
def sum_values(value):
    return round(sum(value.values()), 2)

@register.filter
def sum_values_int(value):
    return int(sum(value.values()))



