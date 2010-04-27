from django.db import models

from immutablefield.models import ImmutableModel

class NoImmutable(ImmutableModel):
    name = models.CharField(max_length=50)


class Simple(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class ImmutableMeta:
        immutable = ('special_id',)


class GoofedUpMeta(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class ImmutableMeta:
        immutable = 'special_id'


class Noisy(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class ImmutableMeta:
        immutable = ('special_id',)
        quiet = False
