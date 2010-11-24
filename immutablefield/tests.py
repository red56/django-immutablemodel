# encoding: utf-8
# encoding: utf-8
from django.db import models
from django.test import TestCase

from immutablefield.models import ImmutableModel

"""
    Test Classes
"""
class NoImmutable(ImmutableModel):
    name = models.CharField(max_length=50)


class SimpleNoSignOffField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class ImmutableMeta:
        immutable = ['special_id']


class SimpleSignOffField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)
    sign_off = models.BooleanField(default=False)

    class ImmutableMeta:
        immutable = ['special_id']
        sign_off_field = 'sign_off'


class ComplexSignOffField(ImmutableModel):
    sign_off = models.BooleanField(default=True)
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class ImmutableMeta:
        immutable = ['special_id']
        sign_off_field = 'sign_off'


class NoisyNoSignOffField(ImmutableModel):
    special_id = models.IntegerField()

    class ImmutableMeta:
        immutable = ['special_id']
        quiet = False


class NoisySignOffField(ImmutableModel):
    special_id = models.IntegerField()
    sign_off = models.BooleanField(default=False)

    class ImmutableMeta:
        immutable = ['special_id']
        sign_off_field = 'sign_off'
        quiet = False


class NoImmutableMetaTest(TestCase):
    def setUp(self):
        self.obj = NoImmutable.objects.create(name='Vader')
    def test__simple(self):
        self.assertTrue(self.obj.name, 'Vader')
        self.obj.name = 'Anakin'
        self.obj.save()

        db_object = SimpleNoSignOffField.objects.all()[0]
        self.assertTrue(self.obj.name, 'Anakin')
        self.assertTrue(db_object.name, 'Anakin')

class CanCreateModelNoSignOffFieldTest(TestCase):
    def setUp(self):
        self.obj = SimpleNoSignOffField.objects.create(
            special_id=1,
            name='Vader',
        )

    def test__simple(self):
        self.assertTrue(self.obj.special_id, 1)
        self.assertTrue(self.obj.name, 'Vader')

        self.obj.special_id = 1000
        self.obj.name = 'Luke'

        self.obj.save()

        db_object = SimpleNoSignOffField.objects.all()[0]
        # Should stay the same, it's immutable. Except the name.
        self.assertTrue(self.obj.special_id, 1)
        self.assertTrue(self.obj.name, 'JarJarBinks')
        self.assertTrue(db_object.special_id, 1)
        self.assertTrue(db_object.name, 'JarJarBinks')

class CanCreateModelSignOffFieldTest(TestCase):
    def setUp(self):
        self.obj = SimpleSignOffField.objects.create(
            special_id=1,
            name='Yoda',
            sign_off=False,
        )

    def test__simple_not_signed_off(self):
        self.assertTrue(self.obj.special_id, 1)
        self.assertTrue(self.obj.name, 'Yoda')

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = SimpleSignOffField.objects.all()[0]

        # Should change, since the signed-off field is false
        self.assertTrue(self.obj.special_id, 1337)
        self.assertTrue(self.obj.name, 'Obi-Wan')
        self.assertTrue(db_object.special_id, 1337)
        self.assertTrue(db_object.name, 'Obi-Wan')

    def test__simple_signed_off(self):
        self.obj.sign_off = True
        self.obj.save()

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = SimpleSignOffField.objects.all()[0]

        # Should not change, since the signed-off field is true
        # Of course, that name is still changable
        self.assertTrue(self.obj.special_id, 1)
        self.assertTrue(self.obj.name, 'Obi-Wan')
        self.assertTrue(self.obj.sign_off, True)
        self.assertTrue(db_object.special_id, 1)
        self.assertTrue(db_object.name, 'Obi-Wan')
        self.assertTrue(db_object.sign_off, True)

class CanCreateModelSignOffFieldInAnyOrderTest(TestCase):
    def setUp(self):
        self.obj = ComplexSignOffField.objects.create(
            special_id=1,
            name='Yoda',
            sign_off=False,
        )

    def test__simple_not_signed_off(self):
        self.assertTrue(self.obj.special_id, 1)
        self.assertTrue(self.obj.name, 'Yoda')

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = ComplexSignOffField.objects.all()[0]

        # Should change, since the signed-off field is false
        self.assertTrue(self.obj.special_id, 1337)
        self.assertTrue(self.obj.name, 'Obi-Wan')
        self.assertTrue(db_object.special_id, 1337)
        self.assertTrue(db_object.name, 'Obi-Wan')

    def test__simple_signed_off(self):
        self.obj.sign_off = True
        self.obj.save()

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = ComplexSignOffField.objects.all()[0]

        # Should not change, since the signed-off field is true
        # Of course, that name is still changable
        self.assertTrue(self.obj.special_id, 1)
        self.assertTrue(self.obj.name, 'Obi-Wan')
        self.assertTrue(self.obj.sign_off, True)
        self.assertTrue(db_object.special_id, 1)
        self.assertTrue(db_object.name, 'Obi-Wan')
        self.assertTrue(db_object.sign_off, True)

class WillRaiseErrorsTest(TestCase):
    def setUp(self):
        self.no_sign_off_field = NoisyNoSignOffField.objects.create(
            special_id=1,
        )
        self.sign_off_field = NoisySignOffField.objects.create(
            special_id=5,
        )

    def test__simple(self):
        self.assertTrue(self.no_sign_off_field.special_id, 1)
        self.assertTrue(self.sign_off_field.special_id, 5)

        self.assertRaises( ValueError,
            setattr,
            self.no_sign_off_field,
            'special_id', 1337,
        )

        self.sign_off_field.special_id = 1000
        self.sign_off_field.sign_off = True
        self.sign_off_field.save()

        self.assertRaises( ValueError,
            setattr,
            self.sign_off_field,
            'special_id', 1337,
        )
