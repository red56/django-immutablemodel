# encoding: utf-8
from django.db import models
from django.core.exceptions import ImproperlyConfigured

models.options.DEFAULT_NAMES += (
    'immutable',
    'immutable_sign_off_field',
    'immutable_quiet',
    'immutable_is_deletable',
    'immutable_cascade_signoff',
)

try:
    from django.conf import settings
except ImportError:
    settings.IMMUTABLE_QUIET = True

class CantDeleteImmutableException(Exception): pass

class ImmutableModel(models.Model):
    def __init__(self,*args,**kwargs):
        super(ImmutableModel, self).__init__(*args,**kwargs)

        if not isinstance(self.immutable, list):
            raise TypeError('immutable attribute in ImmutableMeta must be '
                            'a list')

        if not (isinstance(self.immutable_sign_off_field, basestring) or \
            self.immutable_sign_off_field is None):
            raise TypeError('immutable_sign_off_field attribute in '
                            'ImmutableMeta must be a string')

        if not isinstance(self.immutable_quiet, bool):
            raise TypeError('immutable_quiet attribute in ImmutableMeta must '
                            'be boolean')

        if not isinstance(self.immutable_is_deletable, bool):
            raise TypeError('immutable_is_deletable attribute in ImmutableMeta must '
                            'be boolean')

        if not isinstance(self.immutable_cascade_signoff, bool):
            raise TypeError('immutable_cascade_signoff attribute in ImmutableMeta must '
                            'be boolean')

    @property
    def immutable(self):
        return getattr(
            self._meta,
            'immutable',
            [],
        )

    @property
    def immutable_sign_off_field(self):
        return getattr(
            self._meta,
            'immutable_sign_off_field',
            None,
        )

    @property
    def immutable_quiet(self):
        return getattr(
            self._meta,
            'immutable_quiet',
            settings.IMMUTABLE_QUIET,
        )

    @property
    def immutable_is_deletable(self):
        return getattr(
            self._meta,
            'immutable_is_deletable',
            True,
        )

    @property
    def immutable_cascade_signoff(self):
        return getattr(
            self._meta,
            'immutable_cascade_signoff',
            False,
        )

    def can_change_field(self, field_name):
        return field_name not in self.immutable or not self.is_signed_off()

    def __setattr__(self, name, value):
        if not self.can_change_field(name):
            try:
                current_value = getattr(self, name, None)
            except:
                current_value = None
            if current_value is not None and current_value is not '' and \
                getattr(current_value, '_file', 'not_existant') is not None and \
                current_value != value:
                if self.immutable_quiet:
                    return
                raise ValueError('%s is immutable and cannot be changed' % name)
        super(ImmutableModel, self).__setattr__(name, value)

    def _not_signed_off_error(self):
        return u'In order to sign off, %s needs to be Signed Off' % (str(self),)

    def obstacles_for_signoff(self, dict=None):
        class Struct:
            def __init__(self, **entries):
                self.__dict__.update(entries)

        if self.has_sign_off_field():
            errors = {}
            if self._meta.immutable_cascade_signoff:
                if dict is not None:
                    instance = Struct(**dict)
                else:
                    instance = self

                relation_fields = [
                    (f.name, getattr(instance, f.name),) for f in self._meta.fields
                    if isinstance(f, (models.ForeignKey,)) and
                    not f.name.endswith('_ptr') and
                    self.field_has_sign_off_field(
                        getattr(instance, f.name, None),
                    )
                ]

                many_to_many_fields = [
                    f for f in self._meta.many_to_many
                    if isinstance(f, (models.ManyToManyField,)) and
                    not f.name.endswith('_ptr')
                ]

                fields_to_validate = relation_fields + [
                    (f.name, m2m,)
                    for m2m in getattr(instance, f.name, None)
                    if self.field_has_sign_off_field(m2m)
                    for f in many_to_many_fields
                ]

                for field_name, field in fields_to_validate:
                    if not field.is_signed_off():
                        errors[field_name] = field._not_signed_off_error()
            return errors
        else:
            raise ImproperlyConfigured(
                u"Can't check signoffbility of a model without a signoff field."
            )

    def is_signed_off(self):
        if self.has_sign_off_field():
            """
            During the creation of a Django ORM object, as far as we know,
            the object starts with no fields and they are added after the object
            creation. This leads to an object with some fields created and some
            fields to create.
            In the presence of a sign_off field decision,
            if the field does not exists, it can be changed.
            """
            return getattr(self, self.immutable_sign_off_field, True)
        return True

    def has_sign_off_field(self):
        return self.immutable_sign_off_field != None

    def field_has_sign_off_field(self, field):
        if hasattr(field, '_meta'):
            return hasattr(field._meta, 'immutable_sign_off_field')
        else:
            return False

    def delete(self):
        if not self.immutable_is_deletable and self.is_signed_off():
            if self.immutable_quiet:
                return
            else:
                raise CantDeleteImmutableException(
                    "%s is signed_off and cannot be deleted" % self
                )
        super(ImmutableModel, self).delete()

    class Meta:
        abstract = True

