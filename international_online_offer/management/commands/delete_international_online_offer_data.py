from django.core.management import BaseCommand

from international_online_offer.models import TriageData, UserData


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address of the user data to delete')

    def handle(self, *args, **options):
        email = options['email']
        if email:
            user_data_list = UserData.objects.filter(email=email)
            if user_data_list.exists():
                for user_data in user_data_list:
                    triage_data_list = TriageData.objects.filter(hashed_uuid=user_data.hashed_uuid)
                    triage_data_list.delete()
                    user_data.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'All user data and triage data associated with {email} have been deleted.')
                    )  # noqa: E501
            else:
                self.stdout.write(self.style.WARNING('No userData found for this email address. '))
        else:
            self.stdout.write(self.style.ERROR('Please include the email address'))
