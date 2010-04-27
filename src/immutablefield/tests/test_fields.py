import py

from django.db import models

from immutablefield.tests.models import *

def test_missing_immutable_meta_is_ok():
    m = NoImmutable.objects.create(name='Foo')

    assert m


def test_can_create_model():
    m = Simple.objects.create(special_id=1, name='Foo')
    
    assert m.special_id == 1
    assert m.name == 'Foo'

    m.special_id = 1000
    m.name = 'Bar'
    m.save()

    m = Simple.objects.all()[0]

    # Should stay the same, it's immutable
    assert m.special_id == 1
    assert m.name == 'Bar'


def test_catches_meta_syntax_problems():
    py.test.raises(TypeError, GoofedUpMeta.objects.create,
                   special_id=1, name='Foo')


def test_will_raise_error():
    m = Noisy.objects.create(special_id=1)

    assert m.special_id == 1

    py.test.raises(ValueError, setattr, m, 'special_id', 1000)
