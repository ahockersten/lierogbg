"""
Tests for rankings fields
"""
from django.forms import ValidationError
from django.test import TestCase
from rankings.fields import ColorFormField, ColorField

class TestColorFormField(TestCase):
    """
    Tests related to ColorFormField
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.cff = ColorFormField()

    def test_clean(self):
        """
        clean() works correctly
        """
        self.cff.required = True
        with self.assertRaises(ValidationError):
            self.cff.clean(value='')

        self.cff.required = False
        self.assertEquals(self.cff.clean(value=''), '')

        self.cff.required = True
        with self.assertRaises(ValidationError):
            self.cff.clean(value='FFFFFF')
        with self.assertRaises(ValidationError):
            self.cff.clean(value='#GGGGGG')
        self.assertEquals(self.cff.clean(value='#ffffff'), 16777215)
        self.assertEquals(self.cff.clean(value='#000000'), 0)

class TestColorField(TestCase):
    """
    Tests related to ColorField
    """
    def setUp(self):
        """
        Creates various needed objects.
        """
        self.cf = ColorField()

    def test_to_python(self):
        """
        to_python() works correctly
        """
        self.assertEquals(self.cf.to_python(16777215), "#FFFFFF")
        self.assertEquals(self.cf.to_python(0), "#000000")
        self.assertEquals(self.cf.to_python(None), None)
        with self.assertRaises(ValidationError):
            self.cf.to_python("foo")

    def test_get_prep_value(self):
        """
        get_prep_value() works correctly
        FIXME this cannot be tested in isolation. Figure out how to test it.
        """
        #with self.assertRaises(ValueError):
        #    self.cf.get_prep_value("foo")
        self.assertEquals(self.cf.get_prep_value(0), 0)
        self.assertEquals(self.cf.get_prep_value("Hej"), "Hej")
        self.assertEquals(self.cf.get_prep_value("#ffffff"), "#ffffff")
        self.assertEquals(self.cf.get_prep_value("2"), "2")
        self.assertEquals(self.cf.get_prep_value(None), None)
        self.assertEquals(self.cf.get_prep_value([None]), [None])

    def test_formfield(self):
        """
        formfield() works correctly
        FIXME there's no fail condition for this?
        """
        self.cf.formfield()
