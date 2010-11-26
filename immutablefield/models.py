# encoding: utf-8
from django.db import models

models.options.DEFAULT_NAMES += (
    'immutable',
    'immutable_sign_off_field',
    'immutable_quiet',
)

try:
    from django.conf import settings
except ImportError:
    settings.IMMUTABLE_QUIET = True


class ImmutableModel(models.Model):
    def __init__(self,*args,**kwargs):
        super(ImmutableModel, self).__init__(*args,**kwargs)

        immutable = getattr(
            self._meta, 'immutable',
            None,
        )
        immutable_sign_off_field = getattr(
            self._meta,
            'immutable_sign_off_field',
            None,
        )

        immutable_quiet = getattr(
            self._meta,
            'immutable_quiet',
            settings.IMMUTABLE_QUIET,
        )

        if not (isinstance(immutable, list) or immutable is None):
            raise TypeError('immutable attribute in ImmutableMeta must be '
                            'a list')

        if not (isinstance(immutable_sign_off_field, basestring) or \
            immutable_sign_off_field is None):
            raise TypeError('immutable_sign_off_field attribute in '
                            'ImmutableMeta must be a string')

        if not isinstance(immutable_quiet, bool):
            raise TypeError('immutable_quiet attribute in ImmutableMeta must '
                            'be boolean')

    def can_change_field(self, field_name):
        if field_name not in getattr(self._meta, 'immutable', []):
            return True

        immutable_sign_off_field = getattr(
            self._meta, 'immutable_sign_off_field',
            None,
        )

        if immutable_sign_off_field is None:
            return False

        """
        During the creation of a Django ORM object, as far as we know,
        the object starts with no fields and they are added after the object
        creation. This leads to an object with some fields created and some
        fields to create.
        In the presence of a sign_off field decision,
        if the field does not exists, it can be changed.
        """
        if hasattr(self, immutable_sign_off_field):
            return not bool(getattr(self, immutable_sign_off_field))
        else:
            return True

    def __setattr__(self, name, value):
        if not self.can_change_field(name):
            try:
                current_value = getattr(self, name, None)
            except:
                current_value = None
            if current_value is not None and current_value is not '' and \
                getattr(current_value, '_file', 'not_existant') is not None and \
                current_value != value:
                if getattr(self._meta, 'immutable_quiet', settings.IMMUTABLE_QUIET):
                    return
                raise ValueError(
                    '%s is immutable and cannot be changed' % name)
        super(ImmutableModel, self).__setattr__(name, value)

    class Meta:
        abstract = True
