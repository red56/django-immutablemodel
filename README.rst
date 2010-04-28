django-immutablefield
=====================

Inspired by a Google search that didn't turn up reusable solution for making
fields immutable inside of a Django model.

Installing
----------

One of the following:

Via the ole' standby::

    easy_install django-immutablefield

Pip::

    pip install django-immutablefield

To install directly from Bitbucket::

    pip install -e hg+http://bitbucket.org/robmadole/django-immutablefield#egg=django-immutablefield

.. hint:: You **do not** need to add anything into Django's ``INSTALLED_APPS``

What does it do
---------------

Allows you to define certain fields as immutable inside of Django models.

It works as a drop-in replacement for Django's own ``Model``.  This means you
can ``ImmutableModel`` even if you don't specify ``ImmutableMeta``.

::

    from django.db import models

    from immutablefield.models import ImmutableModel

    CruiseShip(ImmutableModel):
        name = models.CharField(max_length=50)

        class ImmutableMeta:
            # After ya name a ship, you can't change it matey
            immutable = ['name']

        def __unicode__(self):
            return u'%s' % self.name

Now you can try with all your might, but the field won't change (within reason,
sure this is Python we can do almost anything if we try hard enough)

::

    >>> queen_anne = CruiseShip.objects.create(name='Queen Anne')
    <CruiseShip 'Queen Anne'>
    >>> queen_anne.name = 'King George'
    >>> queen_anne.name
    'Queen Anne'

You can make it complain
------------------------

Change the meta section to include ``quiet = False`` and it will raise a
``ValueError`` if an attempt is made to change this value

::

    class ImmutableMeta:
        # After ya name a ship, you can't change it matey
        immutable = ['name']
        quiet = False

The error is raised as soon as you try and set the field, not when ``save()`` is
called.

::

    >>> queen_anne = CruiseShip.objects.create(name='Queen Anne')
    <CruiseShip 'Queen Anne'>
    >>> queen_anne.name = 'King George'
    ValueError: name is immutable and cannot be changed

Reference
---------

**ImmutableMeta**

    Specify options that control how immutable fields are handled when
    subclassing the ``ImmutableModel`` class

    ``immutable``

        Tell ``ImmutableModel`` which fields should not be allowed to change.
        This value must be a tuple or a list and contain the names of the fields
        as strings.::

            class ImmutableMeta:
                immutable = ['my_special_id']

        Specify multiple fields::

            class ImmutableMeta:
                immutable = ['my_special_id', 'name', 'foreign_key']
    
    ``quiet``

        If an attempt is made to change an immutable field, should we quietly
        prevent it.

        Set this value to ``False`` to raise a ``ValueError`` when an immutable
        field is changed.::

            class ImmutableMeta:
                immutable = ['my_special_id']
                quiet = False
