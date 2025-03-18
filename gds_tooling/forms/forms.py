from django import forms
from django.conf import settings
from django.forms import Select
from django.template.loader import render_to_string
from django.utils import translation
from django.forms.utils import ErrorList
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext as _

from directory_constants.choices import COUNTRY_CHOICES
from gds_tooling.forms import GDSChoiceField

BLANK_COUNTRY_CHOICE = [('', 'Select a country')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class GDSErrorList(ErrorList):
    template_name = '_error.html'

    def get_context(self):
        ctx = super().get_context()
        ctx.update({'error_class': 'govuk-error-message'})
        return ctx


class FormMixin:
    use_required_attribute = False
    error_css_class = 'form-group-error'
    error_summary_heading = None

    def __init__(self, is_gds_form=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_gds_form = is_gds_form

    def __str__(self):
        return render_to_string('form.html', {'form': self})


class GDSFormMixin:
    use_required_attribute = False
    error_css_class = 'govuk-form-group--error'
    error_summary_heading = None

    def __init__(self, is_gds_form=True, error_class=GDSErrorList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_gds_form = is_gds_form
        self.error_class = error_class


class Form(FormMixin, forms.Form):
    pass


class GDSForm(GDSFormMixin, forms.Form):
    def __str__(self):
        return render_to_string('_form.html', self.get_context())


class GDSConditionalRevealForm(GDSFormMixin, forms.Form):

    def get_errors(self, bound_field):
        return self.error_class(bound_field.errors, renderer=self.renderer)
    
    def get_errors_str(self, bound_field_errors):
        errors_str = str(bound_field_errors)
        if not isinstance(errors_str, SafeString):
            errors_str = mark_safe(errors_str)
        return errors_str
    
    def get_linked_conditional_fields(self, bound_field):
        pass

    def get_context(self):
        fields = []
        hidden_fields = []
        top_errors = self.non_field_errors().copy()
        for name, bf in self._bound_items():
            bf_errors = self.get_errors(bf)
            if bf.is_hidden:
                if bf_errors:
                    top_errors += [
                        _("(Hidden field %(name)s) %(error)s")
                        % {"name": name, "error": str(e)}
                        for e in bf_errors
                    ]
                hidden_fields.append(bf)
            else:
                errors_str = self.get_errors_str(bf_errors)
                # Create a list of linked conditional reveal fields.
                linked_conditional_reveal_fields = []
                linked_conditional_reveal_choice = 'yes'
                if hasattr(bf.field, 'linked_conditional_reveal_fields'):
                    if hasattr(bf.field, 'linked_conditional_reveal_choice'):
                        linked_conditional_reveal_choice = bf.field.linked_conditional_reveal_choice
                    for linked_conditional_reveal_field_name in bf.field.linked_conditional_reveal_fields:
                        for name, linked_bf in self._bound_items():
                            linked_bf_errors = self.get_errors(linked_bf)
                            linked_bf_error_str = self.get_errors_str(linked_bf_errors)
                            if linked_conditional_reveal_field_name == name:
                                linked_conditional_reveal_fields.append((linked_bf, linked_bf_error_str))
                bf.field.widget.linked_conditional_reveal_fields = linked_conditional_reveal_fields
                bf.field.widget.linked_conditional_reveal_choice = linked_conditional_reveal_choice

                fields.append((bf, errors_str))
        
        return {
            "form": self,
            "fields": fields,
            "hidden_fields": hidden_fields,
            "errors": top_errors,
        }
    

    def __str__(self):
        return render_to_string('_form.html', self.get_context())

    def visible_fields(self):
        """
        Return a list of BoundField objects that aren't hidden fields.
        The opposite of the hidden_fields() method.
        """
        return [field for field in self if not field.is_hidden and not field.field.linked_conditional_reveal]

    def is_hidden_reveal_fields(self):
        """
        Return a list of all the BoundField objects that are hidden fields.
        Useful for manual form layout in templates.
        """
        return [field for field in self if field.field.linked_conditional_reveal]


class LanguageForm(forms.Form):
    lang = GDSChoiceField(widget=Select(attrs={'id': 'great-header-language-select'}), choices=[])  # set by __init__

    def __init__(self, language_choices=settings.LANGUAGES, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lang'].choices = language_choices

    def is_language_available(self, language_code):
        language_codes = [code for code, _ in self.fields['lang'].choices]
        return language_code in language_codes


def get_language_form_initial_data():
    return {'lang': translation.get_language()}
