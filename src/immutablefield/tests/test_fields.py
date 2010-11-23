# encoding: utf-8
import py

from immutablefield.tests.models import *

def test_missing_immutable_meta_is_ok():
    m = NoImmutable.objects.create(name='Foo')

    assert m


def test_can_create_model_no_sign_off_field():
    m = SimpleNoSignOffField.objects.create(special_id=1, name='Foo')

    assert m.special_id == 1
    assert m.name == 'Foo'

    m.special_id = 1000
    m.name = 'Bar'
    m.save()

    m = SimpleNoSignOffField.objects.all()[0]

    # Should stay the same, it's immutable. Except the name.
    assert m.special_id == 1
    assert m.name == 'Bar'


def test_can_create_model_sign_off_field():
    m = SimpleSignOffField.objects.create(
        special_id=1,
        name='Foo',
    )

    assert m.special_id == 1
    assert m.name == 'Foo'

    m.special_id = 1000
    m.name = 'BarM'
    m.save()

    m = SimpleSignOffField.objects.all()[0]

    # Should change, since the signed-off field is false
    assert m.special_id == 1000
    assert m.name == 'BarM'

    m.sign_off = True
    m.save()

    m.special_id = 1337
    m.name = 'Bar'
    m.save()

    m = SimpleSignOffField.objects.all()[0]

    # Should not be changed, except the name
    assert m.special_id == 1000
    assert m.name == 'Bar'


def test_can_only_create_model_sign_off_field():
    m = ComplexSignOffField.objects.create(
        special_id=1,
        name='Foo',
    )

    assert m.sign_off == True
    assert m.special_id == 1
    assert m.name == 'Foo'

    m = ComplexSignOffField.objects.all()[0]
    m.id = 1000
    m.name = 'NewFoo'

    assert m.special_id == 1
    assert m.name == 'NewFoo'


def test_will_raise_error():
    m = NoisyNoSignOffField.objects.create(special_id=1)

    assert m.special_id == 1

    py.test.raises(ValueError, setattr, m, 'special_id', 1000)

    m2 = NoisySignOffField.objects.create(special_id=5)

    assert m2.special_id == 5

    m2.special_id = 1000
    m2.sign_off = True
    m2.save()

    assert m2.special_id == 1000

    m2 = NoisySignOffField.objects.all()[0]

    py.test.raises(ValueError, setattr, m2, 'special_id', 1337)
