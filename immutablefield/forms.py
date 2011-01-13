# encoding: utf-8
from django.forms import ModelForm, BooleanField

def signed_off_model_form_creator(cls):
    class _ImmutableModelForm(ModelForm):
        sign_off = BooleanField(required=False)

        def _wants_to_sign_off(self):
            sign_off = self.cleaned_data.get('sign_off')
            return sign_off is not None and sign_off is True

        def clean(self):
            if self._wants_to_sign_off():
                for key_error, error_msg in self.instance.obstacles_for_signoff(dict=self.cleaned_data).iteritems():
                    self._errors[key_error] = self.error_class([error_msg])
                    del self.cleaned_data[key_error]
            return self.cleaned_data

        class Meta:
            model = cls

    return _ImmutableModelForm
