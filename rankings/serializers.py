"""
Player - Serializers for Django REST Framework
"""

from re import match
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .models import Player

class ColorFormSerializerField(serializers.IntegerField):
    """
    A serializer for ColorField
    """
    default_error_messages = {
        'invalid': _('Enter a valid Color value: e.g. "#ff0022"'),
    }

    def __init__(self, *args, **kwargs):
        super(ColorFormSerializerField, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        if not match('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', data):
            raise serializers.ValidationError(self.error_messages['invalid'])
        data = int(data[1:], 16)
        return super(ColorFormSerializerField, self).to_internal_value(data)


class AllTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('rank', 'rp', 'pp', 'wins', 'losses', 'ties', 'matches',
                  'lives')


class PlayerSerializer(serializers.ModelSerializer):
    ante = serializers.IntegerField(source='calculate_ranked_ante().ante',
                                    read_only=True)
    color = ColorFormSerializerField()
    season = AllTimeSerializer(source='*') # FIXME implement SeasonSerializer
    allTime = AllTimeSerializer(source='*')

    class Meta:
        model = Player
        fields = ('pk', 'name', 'color', 'ante', 'active', 'season',
                  'allTime')
