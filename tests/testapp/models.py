from django.db import models
from immutablemodel import ImmutableModel

class NoMeta(ImmutableModel):
    name = models.CharField(max_length=50)


class HavingMutableField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        mutable_fields = ['name']


class SimpleNoLockField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        immutable_fields = ['special_id']
        immutable_lock_field = None
        
class SimpleLockField(ImmutableModel):
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)
    is_locked = models.BooleanField(default=False)

    class Meta:
        immutable_fields = ['special_id']
        immutable_lock_field = 'is_locked'


class ComplexLockField(ImmutableModel):
    is_locked = models.BooleanField(default=True)
    special_id = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        immutable_fields = ['special_id']
        immutable_lock_field = 'is_locked'


class NoisyMinimal(ImmutableModel):
    special_id = models.IntegerField()

    class Meta:
        immutable_quiet = False
        
class NoisyNoLockField(ImmutableModel):
    special_id = models.IntegerField()

    class Meta:
        immutable_fields = ['special_id']
        immutable_quiet = False
        immutable_lock_field = None
        

class NoisyLockField(ImmutableModel):
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


class AbstractModelWithAttrs(ImmutableModel):
    mutable_field = models.CharField(max_length=50)
    special_id = models.PositiveIntegerField()
    
    class Meta:
        abstract = True
        mutable_fields = ['mutable_field']
        immutable_is_deletable = False

class InheritingModel(AbstractModelWithAttrs):
    child_field = models.CharField(max_length=50)

class NoisyAbstractModelWithAttrs(AbstractModelWithAttrs):
    class Meta(AbstractModelWithAttrs.Meta):
        immutable_quiet = False
        abstract = True
    
class NoisyInheritingModel(NoisyAbstractModelWithAttrs):
    child_field = models.CharField(max_length=50)

