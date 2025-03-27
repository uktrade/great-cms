import argparse

from django.conf import settings
from django.core.management import BaseCommand

from export_academy.models import Registration
from international_online_offer.models import UserData


class Command(BaseCommand):
    help = 'Obsfucate Personal Details'

    START_INDEX = 1
    END_INDEX = -1
    MASK_CHAR = '*'

    def mask_email_data(self, data):
        if not data:
            return data
        name = data.split('@')[0]
        address = data.split('@')[1]
        name = self.mask_string_data(name)
        address = self.mask_string_data(address)
        return f'{name}@{address}'

    def mask_string_data(self, data):
        if not data:
            return data
        return f'{data[:self.START_INDEX]}{self.MASK_CHAR * len(data[self.START_INDEX:self.END_INDEX])}{data[self.END_INDEX:]}'  # noqa:E501

    def mask_json_data(self, data, fields):
        for field in fields:
            try:
                masked_field = self.mask_string_data(data[field])
                data[field] = masked_field
            except KeyError:
                pass
            else:
                data[field] = masked_field
        return data

    def mask_ukea_registration(self, registration, options):
        registration.email = self.mask_email_data(registration.email)
        registration.first_name = self.mask_string_data(registration.first_name)
        registration.last_name = self.mask_string_data(registration.last_name)
        registration.mobile_phone_number = self.mask_string_data(registration.mobile_phone_number)
        registration.data = self.mask_json_data(
            registration.data,
            [
                'first_name',
                'last_name',
                'phone_number',
                'business_postcode',
                'business_name',
                'business_address_line_1',
            ],
        )

        if options['dry_run'] is False:
            registration.save()

    def mask_ioo_user_data(self, user_data, options):
        user_data.company_name = self.mask_string_data(user_data.company_name)
        user_data.company_location = self.mask_string_data(user_data.company_location)
        user_data.duns_number = self.mask_string_data(user_data.duns_number)
        user_data.address_line_1 = self.mask_string_data(user_data.address_line_1)
        user_data.address_line_2 = self.mask_string_data(user_data.address_line_2)
        user_data.town = self.mask_string_data(user_data.town)
        user_data.county = self.mask_string_data(user_data.county)
        user_data.postcode = self.mask_string_data(user_data.postcode)
        user_data.full_name = self.mask_string_data(user_data.full_name)
        user_data.email = self.mask_email_data(user_data.email)
        user_data.telephone_number = self.mask_string_data(user_data.telephone_number)
        user_data.company_website = self.mask_string_data(user_data.company_website)

        if options['dry_run'] is False:
            user_data.save()

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def handle(self, *args, **options):  # noqa: C901

        if settings.APP_ENVIRONMENT.lower() == 'production':
            self.stdout.write(self.style.WARNING('Running in Production environment is disabled - exiting'))
            return

        # Obsfucate UKEA Registration Data
        for registration in Registration.objects.all():
            self.mask_ukea_registration(registration, options)

        # Obsfucate International Online Offer Data
        for user_data in UserData.objects.all():
            self.mask_ioo_user_data(user_data, options)

        if options['dry_run'] is True:
            self.stdout.write(self.style.WARNING('Dry run -- no data updated.'))

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
