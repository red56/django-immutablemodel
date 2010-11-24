# encoding: utf-8
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

        if not (isinstance(self.immutable, list) or self.immutable is None):
            raise TypeError('immutable attribute in ImmutableMeta must be '
                            'a list')

        if not (isinstance(self.sign_off_field, basestring) or \
                self.sign_off_field is None):
            raise TypeError('sign_off_field attribute in ImmutableMeta must be '
                            'a string')

    def can_change_field(self, obj, field_name):
        if field_name not in self.immutable:
            return True

        if self.sign_off_field is None:
            return False

        """
        During the creation of a Django ORM object, as far as we know,
        the object starts with no fields and they are added after the object
        creation. This leads to an object with some fields created and some
        fields to create.
        In the presence of a sign_off field decision,
        if the field does not exists, it can be changed.
        """
        if hasattr(obj, self.sign_off_field):
            return not bool(getattr(obj, self.sign_off_field))
        else:
            return True

class ImmutableModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        new = super(ImmutableModelBase, cls).__new__(cls, name, bases, attrs)
        immutable_meta = attrs.pop('ImmutableMeta', None)
        setattr(new, '_immutable_meta', ImmutableModelOptions(immutable_meta))

        return new


class ImmutableModel(models.Model):
    __metaclass__ = ImmutableModelBase

    def __setattr__(self, name, value):
        meta = self._immutable_meta
        if not meta.can_change_field(self, name):
            try:
                current_value = getattr(self, name, None)
            except:
                current_value = None
            if current_value is not None and current_value is not '' and \
                current_value != value:
                if meta.quiet:
                    return
                raise ValueError(
                    '%s is immutable and cannot be changed' % name)
        super(ImmutableModel, self).__setattr__(name, value)

    class Meta:
        abstract = True
