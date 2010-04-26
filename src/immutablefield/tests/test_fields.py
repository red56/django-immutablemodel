import py

from django.db import models

from immutablefield import ImmutableModel


def test_can_create_model():
    class MyModel(ImmutableModel):
        special_id = models.IntegerField()

        class Meta:
            immutable_fields = ('special_id',)
