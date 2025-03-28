from django import forms
from django.forms.utils import ErrorList, ErrorDict
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext as _


class GDSErrorList(ErrorList):
    """
    This is used to point field error messaging to the gds __error.html file
    """
    template_name = '_error.html'

    def get_context(self):
        ctx = super().get_context()
        ctx.update({'error_class': 'govuk-error-message'})
        return ctx
    
class GDSErrorDict(ErrorDict):
    """
    This is used to render the the error summary
    """
    template_name = '_error-summary.html'
    
    def __init__(
            self,
            *args,
            disable_auto_focus=False,
            error_title='There was a problem',
            error_description='There was a problem with the form submission',
            renderer=None, 
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.error_title = error_title
        self.disable_auto_focus = disable_auto_focus
        self.error_description = error_description

    def get_context(self):
        context = super().get_context()
        context.update({
            'title': self.error_title,
            'disable_auto_focus': self.disable_auto_focus,
            'description': self.error_description
        })
        return context


class GDSFormMixin:
    use_required_attribute = False

    # Default error options
    error_css_class = 'govuk-form-group--error'
    error_summary_heading = None
    error_title = 'There was a problem'
    error_description = 'There was a problem with the form submission'
    error_disable_auto_focus = False

    def __init__(
            self,
            is_gds_form=True,
            error_class=GDSErrorList,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.is_gds_form = is_gds_form
        self.error_class = error_class


class Form(GDSFormMixin, forms.Form):

    def get_errors(self, bound_field):
        return self.error_class(bound_field.errors, renderer=self.renderer)

    def get_errors_str(self, bound_field_errors):
        errors_str = str(bound_field_errors)
        if not isinstance(errors_str, SafeString):
            errors_str = mark_safe(errors_str)
        return errors_str
    
    def full_clean(self):
        """
        Clean all of self.data and populate self._errors and self.cleaned_data.
        """
        self._errors = GDSErrorDict(
            renderer=self.renderer,
            disable_auto_focus=self.error_disable_auto_focus,
            error_title = self.error_title,
            error_description = self.error_description
            )
        if not self.is_bound:  # Stop further processing.
            return
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed():
            return

        self._clean_fields()
        self._clean_form()
        self._post_clean()

    def create_linked_reveal_option_fields(self, bf):
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

    def get_context(self):
        fields = []
        hidden_fields = []
        top_errors = self.non_field_errors().copy()
        for name, bf in self._bound_items():
            bf_errors = self.get_errors(bf)
            if bf.is_hidden:
                if bf_errors:
                    top_errors += [
                        _('(Hidden field %(name)s) %(error)s') % {'name': name, 'error': str(e)} for e in bf_errors
                    ]
                hidden_fields.append(bf)
            else:
                errors_str = self.get_errors_str(bf_errors)
                self.create_linked_reveal_option_fields(bf)
                fields.append((bf, errors_str))
        ctx = {
            'form': self,
            'fields': fields,
            'hidden_fields': hidden_fields,
            'errors': top_errors,
        }
        return ctx

    def __str__(self):
        return render_to_string('_form.html', self.get_context())

    def visible_fields(self):
        """
        Return a list of BoundField objects that aren't hidden fields and
        are not hide_on_page_load.
        The opposite of the hidden_fields() method.
        """
        return [field for field in self if not field.is_hidden 
                and not field.field.linked_conditional_reveal
                and not field.field.hide_on_page_load
                ]

    def is_hidden_reveal_fields(self):
        """
        Return a list of all the BoundField objects that are linked_conditional_reveal fields.
        Useful for manual form layout in templates.
        """
        return [field for field in self if field.field.linked_conditional_reveal]
    

class ModelForm(Form, forms.ModelForm):
    pass
