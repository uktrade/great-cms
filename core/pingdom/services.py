from django.db import DatabaseError

from core.models import Page


class DatabaseHealthCheck:
    name = "database"

    def check(self):
        try:
            Page.objects.all().exists()
        except DatabaseError as de:
            return False, de
        else:
            return True, ''


health_check_services = (DatabaseHealthCheck,)
