#code by BertrandBordage in dezede project
#https://github.com/dezede/dezede/commit/ed13ccaf34494e71fd913fd785c229052f6acdc8#
# coding: utf-8

from __future__ import unicode_literals
from django.template import Library


register = Library()


@register.simple_tag(takes_context=True)
def get_fieldsets_and_inlines(context):
    adminform = context['adminform']
    model_admin = adminform.model_admin
    adminform = iter(adminform)
    inlines = iter(context['inline_admin_formsets'])

    fieldsets_and_inlines = []
    for choice in model_admin.fieldsets_and_inlines_order:
        if choice == 'f':
            fieldsets_and_inlines.append(('f', next(adminform)))
        elif choice == 'i':
            fieldsets_and_inlines.append(('i', next(inlines)))

    for fieldset in adminform:
        fieldsets_and_inlines.append(('f', fieldset))
    for inline in inlines:
        fieldsets_and_inlines.append(('i', inline))

    return fieldsets_and_inlines



