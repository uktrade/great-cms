from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from wagtail.core.models import Page, Site

from core.models import Tour, TourStep
import tests.unit.domestic.factories
import tests.unit.exportplan.factories


User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        # On start Wagtail provides one page with ID=1 and it's called 'Root page'
        root_page = Page.objects.get(pk=1)
        # On start Wagtail provides one site with ID=1
        site = Site.objects.get(pk=1)

        homepage = tests.unit.domestic.factories.DomesticHomePageFactory(parent=root_page)
        export_plan = tests.unit.exportplan.factories.ExportPlanPageFactory(
            parent=homepage,
            slug='export-plan'
        )
        export_plan_dashboard = tests.unit.exportplan.factories.ExportPlanDashboardPageFactory(
            parent=export_plan,
            slug='dashboard'
        )

        site.root_page = homepage
        site.save()
        # Delete welcome to wagtail page
        Page.objects.filter(pk=2).delete()

        # create te export plan dashboard tour
        Tour.objects.create(
            page=export_plan_dashboard,
            title='Welcome to your export plan',
            button_text='Show me around',
            body=(
                'Choose the best country, decide how to price and market your product or service, plan the financing '
                'you need, and plan for customs and regulations when you export.'
            ),
            steps=[
                TourStep(
                    selector='.exportplan-section-item img',
                    title='Let’s start',
                    body=(
                        'Start your planning from any section you want - we’ll provide you with clear guidance, help, '
                        'actions and next steps.'
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
                        'You can also go back to your learning, or choose any guidance we linked to your export plan '
                        'sections.'
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
                        'Add your product and destination country and we will populate your export plan with useful '
                        'links, hints and data.'
                    ),
                    selector='#exportplan-country-sector-customisation-bar p',
                    position='bottom',
                ),
            ]
        )
