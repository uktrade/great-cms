from django.utils.deprecation import MiddlewareMixin

from export_academy.helpers import is_export_academy_registered


class ExportAcademyRegistrationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/export-academy'):
            user = request.user
            request.is_export_academy_registered = is_export_academy_registered(user)
