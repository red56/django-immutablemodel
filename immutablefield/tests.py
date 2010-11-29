# encoding: utf-8
from django.db import models
from django.test import TestCase

from immutablefield import ImmutableModel, CantDeleteImmutableException

"""
    Test Classes
"""
class NoImmutable(ImmutableModel):
    name = models.CharField(max_length=50)


class SimpleNoSignOffField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        immutable = ['special_id']


class SimpleSignOffField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)
    sign_off = models.BooleanField(default=False)

    class Meta:
        immutable = ['special_id']
        immutable_sign_off_field = 'sign_off'


class ComplexSignOffField(ImmutableModel):
    sign_off = models.BooleanField(default=True)
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        immutable = ['special_id']
        immutable_sign_off_field = 'sign_off'


class NoisyNoSignOffField(ImmutableModel):
    special_id = models.IntegerField()

    class Meta:
        immutable = ['special_id']
        immutable_quiet = False


class NoisySignOffField(ImmutableModel):
    special_id = models.IntegerField()
    sign_off = models.BooleanField(default=False)

    class Meta:
        immutable = ['special_id']
        immutable_sign_off_field = 'sign_off'
        immutable_quiet = False


class NoMetaTest(TestCase):
    def setUp(self):
        self.obj = NoImmutable.objects.create(name='Vader')

    def test__simple(self):
        self.assertTrue(self.obj.name, 'Vader')
        self.obj.name = 'Anakin'
        self.obj.save()

        db_object = NoImmutable.objects.all()[0]
        self.assertTrue(self.obj.name, 'Anakin')
        self.assertTrue(db_object.name, 'Anakin')

    def test__delete(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(NoImmutable.objects.all()),
        )


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

    def test__delete(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(SimpleNoSignOffField.objects.all()),
        )

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

    def test__delete_not_signed_off(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(SimpleSignOffField.objects.all()),
        )

    def test__delete_signed_off(self):
        self.obj.sign_off = True
        self.obj.save()
        self.obj.delete()
        self.assertEqual(
            1,
            len(SimpleSignOffField.objects.all()),
        )


class CanCreateModelSignOffFieldInAnyOrderTest(TestCase):
    def setUp(self):
        self.obj = ComplexSignOffField.objects.create(
            sign_off=False,
            special_id=1,
            name='Yoda',
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

    def test__sign_off_field_true_at_create(self):
        sign_off_true_at_first = ComplexSignOffField.objects.create(
            sign_off=True,
            special_id=100,
            name='Yoda',
        )

        self.assertEqual(
            sign_off_true_at_first.special_id,
            100,
        )

        self.assertEqual(
            sign_off_true_at_first.sign_off,
            True,
        )

        self.assertEqual(
            sign_off_true_at_first.name,
            'Yoda',
        )

        sign_off_true_at_first.special_id = 1337
        sign_off_true_at_first.name = 'Obi-Wan'
        sign_off_true_at_first.save()

        db_object = ComplexSignOffField.objects.get(special_id=100)

        # Should not change, since the signed-off field is true
        # Of course, that name is still changable
        self.assertTrue(sign_off_true_at_first.special_id, 100)
        self.assertTrue(sign_off_true_at_first.name, 'Obi-Wan')
        self.assertTrue(sign_off_true_at_first.sign_off, True)
        self.assertTrue(db_object.special_id, 100)
        self.assertTrue(db_object.name, 'Obi-Wan')
        self.assertTrue(db_object.sign_off, True)

    def test__delete_not_signed_off(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(ComplexSignOffField.objects.all()),
        )

    def test__delete_signed_off(self):
        self.obj.sign_off = True
        self.obj.save()
        self.obj.delete()
        self.assertEqual(
            1,
            len(ComplexSignOffField.objects.all()),
        )


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

    def test__sign_off_field_true_at_create(self):
        sign_off_true_at_first = NoisySignOffField.objects.create(
            sign_off=True,
            special_id=1,
        )

        self.assertEqual(
            sign_off_true_at_first.special_id,
            1,
        )

        self.assertEqual(
            sign_off_true_at_first.sign_off,
            True,
        )

        self.assertRaises( ValueError,
            setattr,
            sign_off_true_at_first,
            'special_id', 1337,
        )

    def test__delete_not_signed_off(self):
        self.no_sign_off_field.delete()
        self.sign_off_field.delete()
        self.assertEqual(
            0,
            len(NoisyNoSignOffField.objects.all()),
        )
        self.assertEqual(
            0,
            len(NoisySignOffField.objects.all()),
        )

    def test__delete_signed_off(self):
        self.sign_off_field.sign_off = True
        self.sign_off_field.save()
        self.assertRaises(
            self.sign_off_field.delete,
            CantDeleteImmutableException,
        )
