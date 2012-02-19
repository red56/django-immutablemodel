# encoding: utf-8
from django.db import models
from django.core.exceptions import ImproperlyConfigured

from django.conf import settings

try:
    IMMUTABLE_QUIET_DEFAULT = settings.IMMUTABLE_QUIET
except AttributeError:
    IMMUTABLE_QUIET_DEFAULT = True

IMMUTABLEFIELD_OPTIONS_DEFAULTS = {
    'immutable': [],
    'immutable_sign_off_field': None,
    'immutable_quiet': IMMUTABLE_QUIET_DEFAULT,
    'immutable_is_deletable': True,
}

class CantDeleteImmutableException(Exception): pass

class _Undefined: pass


class ImmutableModelMeta(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        immutability_options = ImmutableModelMeta.extract_options(attrs.get('Meta', {}))
        registered_model = models.base.ModelBase.__new__(cls, name, bases, attrs)
        ImmutableModelMeta.reinject_options(immutability_options, registered_model)
        ImmutableModelMeta.check_options(registered_model)
        return registered_model

    @staticmethod
    def extract_options(meta):
        immutability_options = {}
        for opt_name in IMMUTABLEFIELD_OPTIONS_DEFAULTS.iterkeys():
            value = getattr(meta, opt_name, _Undefined)
            if value is not _Undefined:
                delattr(meta, opt_name)
            immutability_options[opt_name] = value
        return immutability_options
    
    @staticmethod
    def reinject_options(immutability_options, registered_model):
        for opt_name, value in immutability_options.iteritems():
            if value is _Undefined and getattr(registered_model._meta, opt_name, _Undefined) is _Undefined:
                #only want to use default when registered_model doesn't have a value yet 
                value = IMMUTABLEFIELD_OPTIONS_DEFAULTS[opt_name]
            if value is not _Undefined:
                setattr(registered_model._meta, opt_name, value)

    @staticmethod
    def check_options(model):
        if not isinstance(model._meta.immutable, list):
            raise TypeError('immutable attribute in must be '
                            'a list')

        if not (isinstance(model._meta.immutable_sign_off_field, basestring) or \
            model._meta.immutable_sign_off_field is None):
            raise TypeError('immutable_sign_off_field attribute in '
                            'ImmutableMeta must be a string')

        if not isinstance(model._meta.immutable_quiet, bool):
            raise TypeError('immutable_quiet attribute in ImmutableMeta must '
                            'be boolean')

        if not isinstance(model._meta.immutable_is_deletable, bool):
            raise TypeError('immutable_is_deletable attribute in ImmutableMeta must '
                            'be boolean')
            
class ImmutableModel(models.Model):
    __metaclass__ = ImmutableModelMeta

    def can_change_field(self, field_name):
        return field_name not in self._meta.immutable or not self.is_signed_off()

    def __setattr__(self, name, value):
        if not self.can_change_field(name):
            try:
                current_value = getattr(self, name, None)
            except:
                current_value = None
            if current_value is not None and current_value is not '' and \
                getattr(current_value, '_file', 'not_existant') is not None and \
                current_value != value:
                if self._meta.immutable_quiet:
                    return
                raise ValueError('%s is immutable and cannot be changed' % name)
        super(ImmutableModel, self).__setattr__(name, value)

    def _not_signed_off_error(self):
        return u'In order to sign off, %s needs to be Signed Off' % (str(self),)

    def obstacles_for_signoff(self, dict=None):
        if self.has_sign_off_field():
            errors = {}
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
            return getattr(self, self._meta.immutable_sign_off_field, True)
        return True

    def has_sign_off_field(self):
        return self._meta.immutable_sign_off_field != None

    def field_has_sign_off_field(self, field):
        if hasattr(field, '_meta'):
            return hasattr(field._meta, 'immutable_sign_off_field')
        else:
            return False

    def delete(self):
        if not self._meta.immutable_is_deletable and self.is_signed_off():
            if self._meta.immutable_quiet:
                return
            else:
                raise CantDeleteImmutableException(
                    "%s is signed_off and cannot be deleted" % self
                )
        super(ImmutableModel, self).delete()

    class Meta:
        abstract = True

