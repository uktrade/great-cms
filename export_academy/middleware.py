from django.utils.deprecation import MiddlewareMixin

from export_academy.models import Registration
from sso.models import BusinessSSOUser


class ExportAcademyRegistrationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('export_academy'):
            user = request.user
            if user.is_authenticated and isinstance(user, BusinessSSOUser):
                try:
                    Registration.objects.get(pk=user.email)
                    request.user.is_export_academy_user = True
                except Registration.DoesNotExist:
                    pass
