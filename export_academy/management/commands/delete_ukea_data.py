from django.core.management import BaseCommand

from export_academy.models import Booking, Registration, VideoOnDemandPageTracking


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address of the user ukea data to delete')
        parser.add_argument('--dry-run', action='store_true', help='Only show what would be deleted')

    def handle(self, *args, **options):
        email = options['email']
        dry_run = options['dry_run']
        try:
            registration = Registration.objects.filter(email=email).first()
            if not registration:
                self.stdout.write(self.style.WARNING(f'No registarions found with email: {email} '))
                return
            bookings = Booking.objects.filter(registration=registration)
            vod_trackings = VideoOnDemandPageTracking.objects.filter(user_email=email)

            self.stdout.write(f'Registration ID: {registration.id}')
            self.stdout.write(f'Bookings to delete: {bookings.count()}')
            self.stdout.write(f'VOD tracking entries to delete: {vod_trackings.count()}')

            if dry_run:
                self.stdout.write(self.style.WARNING('Dry run -- no data updated.'))
                return
            bookings.delete()
            vod_trackings.delete()
            registration.delete()
            self.stdout.write(self.style.SUCCESS(f'All UKEA data related to email {email} has been deleted '))
        except Exception as exception:
            self.stdout.write(self.style.ERROR(exception))
