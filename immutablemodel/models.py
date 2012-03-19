# encoding: utf-8
from django.db import models


class Option(object):
    def __init__(self, name, default=None):
        self.name = name
        self.default = default
        
    def get_default_for(self, model_class):
        return self.default

class QuietOption(Option):
    def get_default_for(self, model_class):
        from django.conf import settings
        try:
            IMMUTABLE_QUIET_DEFAULT = settings.IMMUTABLE_QUIET
        except AttributeError:
            IMMUTABLE_QUIET_DEFAULT = True
        return IMMUTABLE_QUIET_DEFAULT

class FieldsOption(Option):
    def get_default_for(self, model_class):
        return []


class CantDeleteImmutableException(Exception): pass

class _Undefined: pass

class PK_FIELD: pass

IMMUTABLEFIELD_OPTIONS = dict([(opt.name, opt) for opt in (
    FieldsOption('mutable_fields'),
    FieldsOption('immutable_fields'),
    QuietOption('immutable_quiet'),
    Option('immutable_lock_field', default=PK_FIELD),
    Option('immutable_is_deletable', default=True),
    )])
    

class ImmutableModelMeta(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        super_new = super(ImmutableModelMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, ImmutableModelMeta)]
        if not parents:
            # If this isn't a **sub**class of ImmutableMeta (ie. probably ImmutableModel itself), don't do anything special.
            return super_new(cls, name, bases, attrs)

        immutability_options = ImmutableModelMeta.extract_options(attrs.get('Meta', {}))
        registered_model = models.base.ModelBase.__new__(cls, name, bases, attrs)
        ImmutableModelMeta.reinject_options(immutability_options, registered_model)
        ImmutableModelMeta.check_options(registered_model)
        return registered_model

    @staticmethod
    def extract_options(meta):
        if getattr(meta, "immutable", _Undefined) is not _Undefined:
            raise ValueError("immutable is not an option for ImmutableModels - use immutable_fields instead")
        immutability_options = {}
        for opt_name in IMMUTABLEFIELD_OPTIONS:
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
                value = IMMUTABLEFIELD_OPTIONS[opt_name].get_default_for(registered_model)
            if value is not _Undefined:
                setattr(registered_model._meta, opt_name, value)

    @staticmethod
    def check_options(model):
        if model._meta.abstract:
            return
        if not isinstance(model._meta.immutable_fields, list):
            raise TypeError('immutable_fields attribute in %s must be '
                            'a list' % model)
        if not isinstance(model._meta.mutable_fields, list):
            raise TypeError('mutable_fields attribute in %s must be '
                            'a list' % model)
        
        if model._meta.mutable_fields and model._meta.immutable_fields:
            raise ValueError('You can specify either mutable_fields OR immutable_fields in %s (not both)' % model)
        if model._meta.immutable_fields:
            model._meta.mutable_fields = [f.name for f in model._meta.fields if f.name not in model._meta.immutable_fields]
        
        # we'll keep immutable_fields, but just as the reverse of mutable fields:
        model._meta.immutable_fields = [f.name for f in model._meta.fields if f.name not in model._meta.mutable_fields]
        
        if model._meta.immutable_lock_field is PK_FIELD:
            model._meta.immutable_lock_field = model._meta.pk.name
        elif (isinstance(model._meta.immutable_lock_field, basestring) or 
            model._meta.immutable_lock_field is None
            ):
            pass
        else:
            raise TypeError('immutable_lock_field attribute in '
                            '%s must be a string (or None, or omitted)' % model)
        
        
        if not isinstance(model._meta.immutable_quiet, bool):
            raise TypeError('immutable_quiet attribute in %s must '
                            'be boolean' % model)

        if not isinstance(model._meta.immutable_is_deletable, bool):
            raise TypeError('immutable_is_deletable attribute in %s must '
                            'be boolean' % model)
            
class ImmutableModel(models.Model):
    __metaclass__ = ImmutableModelMeta

    def can_change_field(self, field_name):
        return field_name in self._meta.mutable_fields or not self.is_immutable()

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

    def is_immutable(self):
        if self.has_immutable_lock_field():
            """
            During the creation of a Django ORM object, as far as we know,
            the object starts with no fields and they are added after the object
            creation. This leads to an object with some fields created and some
            fields to create.
            In the presence of a immutable_lock field decision,
            if the field does not exists, it can be changed.
            """
            return getattr(self, self._meta.immutable_lock_field, True)
        return True

    def has_immutable_lock_field(self):
        return self._meta.immutable_lock_field != None

    def delete(self):
        if not self._meta.immutable_is_deletable and self.is_immutable():
            if self._meta.immutable_quiet:
                return
            else:
                raise CantDeleteImmutableException(
                    "%s is immutable and cannot be deleted" % self
                )
        super(ImmutableModel, self).delete()

    class Meta:
        abstract = True

