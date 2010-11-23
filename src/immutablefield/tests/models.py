# encoding: utf-8
from django.db import models

from immutablefield.models import ImmutableModel

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
