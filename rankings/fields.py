"""
Custom form fields
"""
import re
from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ColorFormField(forms.IntegerField):
    """
    A form field for describing a color as hex.
    """
    default_error_messages = {
        'invalid': _('Enter a valid Color value: e.g. "#ff0022"'),
    }

    def __init__(self, *args, **kwargs):
        super(ColorFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if value == '' and not self.required:
            return ''
        if not re.match('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            raise forms.ValidationError(self.error_messages['invalid'])
        value = int(value[1:], 16)
        super(ColorFormField, self).clean(value)
        return value


class ColorField(models.PositiveIntegerField):
    """
    A field for entering a color as hex.
    """
    description = _("Hex value for a color")

    def __init__(self, *args, **kwargs):
        super(ColorField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        super(ColorField, self).to_python(value)

        try:
            string = hex(value)[2:]

            return "#" + string.zfill(6).upper()
        except TypeError:
            return None

    def get_prep_value(self, value):
        try:
            # hex to int, save the int representation of the Color hex code
            # to the database
            return value
        except ValueError:
            return None

    def formfield(self, *args, **kwargs):
        kwargs['form_class'] = ColorFormField
        return super(ColorField, self).formfield(*args, **kwargs)
