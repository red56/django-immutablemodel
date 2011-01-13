# encoding: utf-8
from django.contrib import admin

class ImmutableModelAdmin(admin.ModelAdmin):
    def validate_and_check_immutable_sign_off_field(self, obj):
        try:
            setattr(obj, obj._meta.immutable_sign_off_field, True)
        except AttributeError:
            pass

        obj.save()

    def _validate_and_check_immutable_sign_off_request(self, request, obj):
        if 'sign_off' in request.POST and request.POST['sign_off'] == 'on':
            self.validate_and_check_immutable_sign_off_field(obj)

    def response_change(self, request, obj):
        response = super(ImmutableModelAdmin, self).response_change(request,obj)
        self._validate_and_check_immutable_sign_off_request(request, obj)

        return response

    def response_add(self, request, obj):
        response = super(ImmutableModelAdmin, self).response_add(request,obj)
        self._validate_and_check_immutable_sign_off_request(request, obj)

        return response
