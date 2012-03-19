# encoding: utf-8
from django.test import TestCase

from testapp.models import *
from immutablemodel.models import CantDeleteImmutableException

class Case01_NoMetaTest(TestCase):
    def setUp(self):
        self.obj = NoMeta.objects.create(name='Vader')

    def test01_cant_change_once_saved(self):
        """A model with no meta should have all the fields immutable"""
        self.assertEqual(self.obj.name, 'Vader')
        self.obj.name = 'Anakin'
        self.obj.save()

        db_object = NoMeta.objects.all()[0]
        self.assertEqual(self.obj.name, 'Vader')
        self.assertEqual(db_object.name, 'Vader')

    def test02_can_change_before_save_by_default(self):
        obj = NoMeta(name='Anakin')
        obj.name = 'Darth'
        obj.save()
        self.assertEqual(obj.name, 'Darth')
        
    def test03_delete(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(NoMeta.objects.all()),
        )


class Case02_CanCreateModelNoSignOffFieldTest(TestCase):
    def setUp(self):
        self.obj = SimpleNoSignOffField.objects.create(
            special_id=1,
            name='Vader',
        )

    def test__simple(self):
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Vader')

        self.obj.special_id = 1000
        self.obj.name = 'Luke'

        self.obj.save()

        db_object = SimpleNoSignOffField.objects.all()[0]
        # Should stay the same, it's immutable. Except the name.
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Luke')
        self.assertEqual(db_object.special_id, 1)
        self.assertEqual(db_object.name, 'Luke')

    def test__delete(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(SimpleNoSignOffField.objects.all()),
        )
class Case03_HavingMutableField_Test(TestCase):
    def setUp(self):
        self.obj = HavingMutableField.objects.create(
            special_id=1,
            name='Vader',
        )

    def test__simple(self):
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Vader')

        self.obj.special_id = 1000
        self.obj.name = 'Luke'

        self.obj.save()

        db_object = HavingMutableField.objects.all()[0]
        # Should stay the same, it's immutable. Except the name.
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Luke')
        self.assertEqual(db_object.special_id, 1)
        self.assertEqual(db_object.name, 'Luke')


class Case03_CanCreateModelSignOffFieldTest(TestCase):
    def setUp(self):
        self.obj = SimpleSignOffField.objects.create(
            special_id=1,
            name='Yoda',
            is_locked=False,
        )

    def test__simple_not_locked(self):
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Yoda')

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = SimpleSignOffField.objects.all()[0]

        # Should change, since the lock field is false
        self.assertEqual(self.obj.special_id, 1337)
        self.assertEqual(self.obj.name, 'Obi-Wan')
        self.assertEqual(db_object.special_id, 1337)
        self.assertEqual(db_object.name, 'Obi-Wan')

    def test__simple_locked(self):
        self.obj.is_locked = True
        self.obj.save()

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = SimpleSignOffField.objects.all()[0]

        # Should not change, since the lock field is true
        # Of course, that name is still changable
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Obi-Wan')
        self.assertEqual(self.obj.is_locked, True)
        self.assertEqual(db_object.special_id, 1)
        self.assertEqual(db_object.name, 'Obi-Wan')
        self.assertEqual(db_object.is_locked, True)

    def test__delete_not_locked(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(SimpleSignOffField.objects.all()),
        )

    def test__delete_locked(self):
        self.obj.is_locked = True
        self.obj.save()
        self.obj.delete()
        self.assertEqual(
            0,
            len(SimpleSignOffField.objects.all()),
        )


class Case04_CanCreateModelSignOffFieldInAnyOrderTest(TestCase):
    def setUp(self):
        self.obj = ComplexSignOffField.objects.create(
            is_locked=False,
            special_id=1,
            name='Yoda',
        )

    def test__simple_not_locked(self):
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Yoda')

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = ComplexSignOffField.objects.all()[0]

        # Should change, since the lock field is false
        self.assertEqual(self.obj.special_id, 1337)
        self.assertEqual(self.obj.name, 'Obi-Wan')
        self.assertEqual(db_object.special_id, 1337)
        self.assertEqual(db_object.name, 'Obi-Wan')

    def test__simple_locked(self):
        self.obj.is_locked = True
        self.obj.save()

        self.obj.special_id = 1337
        self.obj.name = 'Obi-Wan'
        self.obj.save()

        db_object = ComplexSignOffField.objects.all()[0]

        # Should not change, since the lock field is true
        # Of course, that name is still changable
        self.assertEqual(self.obj.special_id, 1)
        self.assertEqual(self.obj.name, 'Obi-Wan')
        self.assertEqual(self.obj.is_locked, True)
        self.assertEqual(db_object.special_id, 1)
        self.assertEqual(db_object.name, 'Obi-Wan')
        self.assertEqual(db_object.is_locked, True)

    def test__lock_field_true_at_create(self):
        is_locked_at_first = ComplexSignOffField.objects.create(
            is_locked=True,
            special_id=100,
            name='Yoda',
        )

        self.assertEqual(
            is_locked_at_first.special_id,
            100,
        )

        self.assertEqual(
            is_locked_at_first.is_locked,
            True,
        )

        self.assertEqual(
            is_locked_at_first.name,
            'Yoda',
        )

        is_locked_at_first.special_id = 1337
        is_locked_at_first.name = 'Obi-Wan'
        is_locked_at_first.save()

        db_object = ComplexSignOffField.objects.get(special_id=100)

        # Should not change, since the lock field is true
        # Of course, that name is still changable
        self.assertEqual(is_locked_at_first.special_id, 100)
        self.assertEqual(is_locked_at_first.name, 'Obi-Wan')
        self.assertEqual(is_locked_at_first.is_locked, True)
        self.assertEqual(db_object.special_id, 100)
        self.assertEqual(db_object.name, 'Obi-Wan')
        self.assertEqual(db_object.is_locked, True)

    def test__delete_not_locked(self):
        self.obj.delete()
        self.assertEqual(
            0,
            len(ComplexSignOffField.objects.all()),
        )

    def test__delete_locked(self):
        self.obj.is_locked = True
        self.obj.save()
        self.obj.delete()
        self.assertEqual(
            0,
            len(ComplexSignOffField.objects.all()),
        )

class Case05_QuietCannotDelete(TestCase):
    def setUp(self):
        self.not_deletable_quiet = QuietNotDeletable.objects.create(
            special_id=1337,
        )

    def test_no_delete(self):
        self.not_deletable_quiet.delete()
        self.assertEqual(
            1,
            len(QuietNotDeletable.objects.all()),
        )

class Case06_WillRaiseErrorsTest(TestCase):
    def setUp(self):
        self.no_lock_field = NoisyNoSignOffField.objects.create(
            special_id=1,
        )
        self.lock_field = NoisySignOffField.objects.create(
            special_id=5,
        )
        self.not_deletable_noisy = NoisyNotDeletable.objects.create(
            special_id=1123,
        )

    def test__simple(self):
        self.assertEqual(self.no_lock_field.special_id, 1)
        self.assertEqual(self.lock_field.special_id, 5)

        self.assertRaises( ValueError,
            setattr,
            self.no_lock_field,
            'special_id', 1337,
        )

        self.lock_field.special_id = 1000
        self.lock_field.is_locked = True
        self.lock_field.save()

        self.assertRaises( ValueError,
            setattr,
            self.lock_field,
            'special_id', 1337,
        )

    def test__lock_field_true_at_create(self):
        is_locked_at_first = NoisySignOffField.objects.create(
            is_locked=True,
            special_id=1,
        )

        self.assertEqual(
            is_locked_at_first.special_id,
            1,
        )

        self.assertEqual(
            is_locked_at_first.is_locked,
            True,
        )

        self.assertRaises( ValueError,
            setattr,
            is_locked_at_first,
            'special_id', 1337,
        )

    def test__delete_not_locked(self):
        self.no_lock_field.delete()
        self.lock_field.delete()

        self.assertRaises(
            CantDeleteImmutableException,
            self.not_deletable_noisy.delete,
        )
        self.assertEqual(
            0,
            len(NoisyNoSignOffField.objects.all()),
        )
        self.assertEqual(
            0,
            len(NoisySignOffField.objects.all()),
        )

    def test__delete_locked(self):
        self.lock_field.is_locked = True
        self.lock_field.save()
        self.lock_field.delete()
        self.assertEqual(
            0,
            len(NoisySignOffField.objects.all()),
        )

class Case07_InheritenceTests(TestCase):
    
    def test01_defaults_work_for_abstract(self):
        c = ChildModel(parent_field="parent", child_field="child")
        c.save()
        c.child_field="other"
        c.parent_field="other"
        c.save()
        db_object = ChildModel.objects.all()[0]
        for t, name in [(c, 'c'), (db_object, 'db_object')]:
            self.assertEqual(t.child_field, "child", "expecting %s.child_field" % name)
            self.assertEqual(t.parent_field, "parent", "expecting %s.parent_field" % name)

    def test02_can_inherit_attributes(self):
        c = InheritingModel(child_field="child", mutable_field="whatever", special_id=1)
        c.save()
        c.child_field="other"
        c.special_id=47
        c.mutable_field="other"
        c.save()
        db_object = InheritingModel.objects.get(pk=c.id)
        for t, name in [(c, 'c'), (db_object, 'db_object')]:
            self.assertEqual(t.child_field, "child", "expecting %s.child_field" % name)
            self.assertEqual(t.special_id, 1, "expecting %s.special_id" % name)
            self.assertEqual(t.mutable_field, "other", "expecting %s.mutable_field" % name)
    
