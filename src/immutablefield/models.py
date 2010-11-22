from django.db import models
from django.db.models.base import ModelBase

try:
    from django.conf.settings import IMMUTABLE_QUIET
except ImportError:
    IMMUTABLE_QUIET = True

class ImmutableModelOptions(object):
    immutable = []
    sign_off_field = None
    quiet = IMMUTABLE_QUIET

    def __init__(self, opts):
        if not opts: return

        for key, value in opts.__dict__.iteritems():
            setattr(self, key, value)

        if isinstance(self.immutable, basestring):
            raise TypeError('immutable attribute in ImmutableMeta must be '
                            'iterable and not a string')

    def can_change_field(self, obj, field_name):
        if field_name not in self.immutable:
            return True

        if sign_off_field is None:
            return False

        return bool(getattr(obj,sign_off_field))

class ImmutableModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        new = super(ImmutableModelBase, cls).__new__(cls, name, bases, attrs)
        immutable_meta = attrs.pop('ImmutableMeta', None)
        setattr(new, '_immutable_meta', ImmutableModelOptions(immutable_meta))

        return new


class ImmutableModel(models.Model):
    """
    Use this as the base of your model to enable immutable field support

    Example::

        MyModel(ImmutableModel):
            special_id = models.CharField(max_length=64, primary_key=True)

            class ImmutableMeta:
                immutable = ['special_id']

            def __unicode__(self):
                return u'%s' % self.special_id

    Create an instance::

        >>> thing = MyModel.objects.create(special_id='123456789asdfgjkl')
        <MyModel '1234567890asdfgjkl'>
        >>> thing.special_id
        '1234567890asdfgjkl'
        >>> thing.special_id = 'somethingElse'
        >>> thing.save()
        >>> thing.special_id
        '1234567890asdfgjkl'
    """
    __metaclass__ = ImmutableModelBase

    def __setattr__(self, name, value):
        meta = self._immutable_meta
        if not meta.can_change_field(self, name):
            try:
                current_value = getattr(self, name, None)
            except:
                current_value = None
            if current_value is not None and current_value is not '':
                if meta.quiet:
                    return
                raise ValueError(
                    '%s is immutable and cannot be changed' % name)
        super(ImmutableModel, self).__setattr__(name, value)

    class Meta:
        abstract = True
