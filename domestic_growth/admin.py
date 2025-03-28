import csv

from django import forms
from django.contrib import admin
from django.forms.widgets import ClearableFileInput
from django.shortcuts import redirect, render
from django.urls import path

from domestic_growth.models import DomesticGrowthContent


class FileUploadWidget(ClearableFileInput):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs'].setdefault('accept', '.csv')
        return context


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(widget=FileUploadWidget)


@admin.register(DomesticGrowthContent)
class DomesticGrowthContentDjangoAdminModel(admin.ModelAdmin):
    """
    Class that enables display of DomesticGrowthContent objects in django admin and facilitates bulk create
    via .csv upload.
    """

    change_list_template = 'admin/domestic-growth-content-changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        return [
            path('import-csv/', self.import_csv),
        ] + urls

    def import_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES['csv_file']

            if '.csv' not in csv_file.name:
                raise Exception('Only processes .csv files')
            elif csv_file.size >= (1024 * 1024):
                raise Exception('Only processes files < 1Mb')

            csv_file_contents = csv_file.read().decode(encoding='ISO-8859-1')
            reader = csv.reader(csv_file_contents.splitlines())
            num_imported_or_changed, errored = self.import_domestic_growth_content_snippets(reader)
            status_message = f'{num_imported_or_changed} snippets imported or modified. '
            if len(errored) > 0:
                status_message += f'{len(errored)} errored, IDs = {errored}.'
            self.message_user(request, status_message)
            return redirect('/django-admin/domestic_growth/domesticgrowthcontent')
        form = CsvImportForm()
        payload = {'form': form}
        return render(request, 'admin/csv-upload-form.html', payload)

    def import_domestic_growth_content_snippets(self, domestic_growth_csv_reader: csv.reader):
        num_imported_or_changed = 0
        errored_ids = []
        # skip first row as it is headers
        for snippet in list(domestic_growth_csv_reader)[1:]:
            try:
                DomesticGrowthContent.objects.update_or_create(
                    content_id=snippet[0],
                    defaults={
                        'title': snippet[1],
                        'description': snippet[2],
                        'url': snippet[3],
                        'is_dynamic': snippet[4] == 'Y',
                        'region': snippet[5],
                        'sector': snippet[6],
                    },
                )
                num_imported_or_changed += 1
            except Exception:
                errored_ids.append(snippet[0])

        return num_imported_or_changed, errored_ids
