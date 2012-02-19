from django.db import models
from immutablefield import ImmutableModel, CantDeleteImmutableException

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


class NoisyNotDeletable(ImmutableModel):
    special_id = models.IntegerField()

    class Meta:
        immutable_quiet = False
        immutable_is_deletable = False


class QuietNotDeletable(ImmutableModel):
    special_id = models.IntegerField()

    class Meta:
        immutable_quiet = True
        immutable_is_deletable = False

