# vim: set fdm=marker fileencoding=utf-8 ts=4 sw=4 expandtab :

"""
Custom widgets
"""

from django.forms.utils import flatatt
from django.forms.widgets import Input
from django.utils.encoding import force_text
from django.utils.html import format_html, mark_safe


class CalendarWidget(Input):
    """
    Used to render datepickers appropriately, with picking button and so on.
    This is meant to be attached to DateFields
    """
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))
        spans = mark_safe(
            '<span class="input-group-addon">'
            '<span class="glyphicon glyphicon-calendar"></span></span>')
        input_elem = format_html('<input{} />', flatatt(final_attrs))
        enclosing_div = format_html(
            '<div class="input-group datepicker-input">{} {}</div>',
            input_elem, spans)
        return enclosing_div
    # FIXME add render_js to this, so we don't have to call JS methods
    # manually for datepickers
