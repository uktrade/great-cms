from django.core.management import BaseCommand

from core import models


defaults = dict(
    title='Welcome to your export plan',
    button_text='Show me around',
    body=(
        'Choose the best country, decide how to price and market your product or service, plan the '
        'financing you need, and plan for customs and regulations when you export.'
    ),
    steps=[
        models.TourStep(
            title='Let’s start',
            body=(
                'Start your planning from any section you want - we’ll provide you with clear guidance, '
                'help, actions and next steps.'
            ),
            position='bottom',
            selector='.exportplan-section-item img',
        ),
        models.TourStep(
            title='Collaborate with your team and International Trade Advisers',
            body='If you like, you can share your draft plan with colleagues for them to contribute too.',
            position='bottom',
            selector='#exportplan-collaboraton-menu',
        ),
        models.TourStep(
            title='Learn as you go',
            body=(
                'You can also go back to your learning, or choose any guidance we linked to your export '
                'plan sections.'
            ),
            position='top',
            selector='#exportplan-continue-leaning-title',
        ),
        models.TourStep(
            title='Track your progress',
            body='Complete the actions for each section of your plan and become export ready.',
            position='top',
            selector='#exportplan-completion-progress-indicator',
        ),
        models.TourStep(
            title='Where do you want to export?',
            body=(
                'Add your product and destination country and we will populate your export plan with '
                'useful links, hints and data.'
            ),
            position='bottom',
            selector='#exportplan-country-sector-customisation-bar p',
        ),
    ]
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        export_plan_dashboard = models.DetailPage.objects.filter().get(
            template='exportplan/export_plan_dashboard_page.html'
        )
        if export_plan_dashboard:
            models.Tour.objects.get_or_create(page=export_plan_dashboard, defaults=defaults)
