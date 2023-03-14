import datetime

from django.db import models


class EventQuerySet(models.QuerySet):
    """Handles lazy database lookups for a set of Event objects."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_date = datetime.datetime.now().date()
        self.current_isodate = self.current_date.isocalendar()

    #####################################
    # METHODS THAT MAP TO DJANGO-FILTER #
    #####################################

    def all(self):
        return self

    def today(self):
        return self.filter(start_date__date=self.current_date)

    def tomorrow(self):
        return self.filter(start_date__date=self.current_date + datetime.timedelta(days=1))

    def this_week(self):
        return self.filter(start_date__year=self.current_date.year, start_date__week=self.current_isodate.week)

    def next_week(self):
        return self.filter(start_date__year=self.current_date.year, start_date__week=self.current_isodate.week + 1)

    def this_month(self):
        return self.filter(start_date__year=self.current_date.year, start_date__month=self.current_date.month)

    def next_month(self):
        return self.filter(
            start_date__year__gte=self.current_date.year, start_date__month__gte=self.current_date.month + 1
        )


class EventManager(models.Manager):
    def get_queryset(self):
        # return super().get_queryset().exclude(end_date__lt=datetime.datetime.now())
        return super().get_queryset()
