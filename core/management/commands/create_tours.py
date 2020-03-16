from django.core.management import BaseCommand

from core.models import Tour, TourStep
from exportplan.models import ExportPlanDashboardPage


class Command(BaseCommand):

    def handle(self, *args, **options):
        export_plan_dashboard = ExportPlanDashboardPage.objects.first()
        if export_plan_dashboard:
            defaults = dict(
                title='Welcome to your export plan',
                button_text='Show me around',
                body=(
                    'Choose the best country, decide how to price and market your product or service, plan the '
                    'financing you need, and plan for customs and regulations when you export.'
                ),
                steps=[
                    TourStep(
                        selector='.exportplan-section-item img',
                        title='Let’s start',
                        body=(
                            'Start your planning from any section you want - we’ll provide you with clear guidance, '
                            'help, actions and next steps.'
                        ),
                        position='bottom',
                    ),
                    TourStep(
                        selector='#exportplan-collaboraton-menu',
                        title='Collaborate with your team and International Trade Advisers',
                        body='If you like, you can share your draft plan with colleagues for them to contribute too.',
                        position='bottom',
                    ),
                    TourStep(
                        selector='#exportplan-continue-leaning-title',
                        title='Learn as you go',
                        body=(
                            'You can also go back to your learning, or choose any guidance we linked to your export '
                            'plan sections.'
                        ),
                        position='top',
                    ),
                    TourStep(
                        title='Track your progress',
                        body='Complete the actions for each section of your plan and become export ready.',
                        selector='#exportplan-completion-progress-indicator',
                        position='top',
                    ),
                    TourStep(
                        title='Where do you want to export?',
                        body=(
                            'Add your product and destination country and we will populate your export plan with '
                            'useful links, hints and data.'
                        ),
                        selector='#exportplan-country-sector-customisation-bar p',
                        position='bottom',
                    ),
                ]
            )
            Tour.objects.get_or_create(page=export_plan_dashboard, defaults=defaults)
