import random

from core.models import CMSGenericPage

LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = 'Complete the contact form to keep up to date with our personalised service.'
HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = """Your business qualifies for 1 to 1 support from specialist UK government
 advisors. Complete the form to access this and keep up to date with our personalised service."""
COMPLETED_CONTACT_FORM_MESSAGE = 'Thank you for completing the contact form.'


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
    parent_page_types = ['international_online_offer.IOOLandingPage']
    subpage_types = []
    template_choices = [('ioo/guide.html', 'IOO Guide Page')]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        high_value_investor = random.choice([True, False])
        submit_contact_details_success = request.GET.get('success')
        if not high_value_investor:
            complete_contact_form_message = LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE
        else:
            complete_contact_form_message = HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE

        context.update(
            high_value_investor=high_value_investor,
            complete_contact_form_message=complete_contact_form_message,
            complete_contact_form_link='international_online_offer:contact',
            complete_contact_form_link_text='Complete form',
            completed_contact_form_message=COMPLETED_CONTACT_FORM_MESSAGE,
            submit_contact_details_success=submit_contact_details_success,
        )
        return context
