from django.db import models
from immutablemodel import ImmutableModel

class NoMeta(ImmutableModel):
    name = models.CharField(max_length=50)


class SimpleNoSignOffField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        immutable_fields = ['special_id']


class SimpleSignOffField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)
    is_locked = models.BooleanField(default=False)

    class Meta:
        immutable_fields = ['special_id']
        immutable_lock_field = 'is_locked'


class ComplexSignOffField(ImmutableModel):
    is_locked = models.BooleanField(default=True)
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        immutable_fields = ['special_id']
        immutable_lock_field = 'is_locked'


class NoisyNoSignOffField(ImmutableModel):
    special_id = models.IntegerField()

    class Meta:
        immutable_fields = ['special_id']
        immutable_quiet = False


class NoisySignOffField(ImmutableModel):
    special_id = models.IntegerField()
    is_locked = models.BooleanField(default=False)

    class Meta:
        immutable_fields = ['special_id']
        immutable_lock_field = 'is_locked'
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

class AbstractModel(ImmutableModel):
    parent_field = models.CharField(max_length=50)
    
    class Meta:
        abstract = True
        
class ChildModel(AbstractModel):
    child_field = models.CharField(max_length=50)
