from core.models import CMSGenericPage


class IOOLandingPage(CMSGenericPage):
    parent_page_types = [
        'international_online_offer.IOOLandingPage',
    ]
    subpage_types = [
        'international_online_offer.IOOLandingPage',
        'international_online_offer.IOOGuidePage',
    ]
    template_choices = [('ioo/index.html', 'IOO Landing Page')]


class IOOGuidePage(CMSGenericPage):
    LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = (
        'Complete the contact form to keep up to date with our personalised service.'
    )
    HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = """Your business qualifies for 1 to 1 support from specialist UK
        government advisors. Complete the form to access this and keep up to date with our
        personalised service."""
    CONTACT_FORM_SUCCESS_MESSAGE = 'Thank you for completing the contact form.'
    parent_page_types = ['international_online_offer.IOOLandingPage']
    subpage_types = []
    template_choices = [('ioo/guide.html', 'IOO Guide Page')]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            complete_contact_form_message=self.LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE,
            complete_contact_form_link='international_online_offer:contact',
            complete_contact_form_link_text='Complete form',
            contact_form_success_message=self.CONTACT_FORM_SUCCESS_MESSAGE,
            submit_contact_details_success=request.GET.get('success'),
        )
        return context
