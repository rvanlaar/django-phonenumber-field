#-*- coding: utf-8 -*-

from babel import Locale
from babel.core import UnknownLocaleError

from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE

from django.utils import translation
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget

from phonenumber_field.phonenumber import PhoneNumber


class PhonePrefixSelect(Select):

    initial = None

    def __init__(self, initial=None):
        choices = [('', '---------')]
        language = translation.get_language()
        try:
            locale = Locale(language)
        except UnknownLocaleError:
            return
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            prefix = '+%d' % prefix
            if initial and initial in values:
                self.initial = prefix
            for country_code in values:
                country_name = locale.territories.get(country_code)
                if country_name:
                    choices.append((prefix, u'%s %s' % (country_name, prefix)))
        return super(PhonePrefixSelect, self).__init__(choices=sorted(choices, key=lambda item: item[1]))

    def render(self, name, value, *args, **kwargs):
        return super(PhonePrefixSelect, self).render(name, value or self.initial, *args, **kwargs)

class PhoneNumberPrefixWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - a country select box for phone prefix
    - an input for local phone number
    """
    def __init__(self, attrs=None, initial=None):
        widgets = (PhonePrefixSelect(initial),TextInput(),)
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, PhoneNumber):
            return ['+%d' % value.country_code, value.national_number]
        if value:
            return value.split('.')
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super(PhoneNumberPrefixWidget, self).value_from_datadict(data, files, name)
        return '%s.%s' % tuple(values)