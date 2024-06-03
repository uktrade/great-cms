from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone


class EventQuerySet(models.QuerySet):
    """Handles lazy database lookups for a set of Event objects."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_date = timezone.now().date()
        self.current_isodate = self.current_date.isocalendar()

    #####################################
    # METHODS THAT MAP TO DJANGO-FILTER #
    #####################################

    def all(self):
        return self

    def today(self):
        return self.filter(start_date__date=self.current_date)

    def tomorrow(self):
        return self.filter(start_date__date=self.current_date + timedelta(days=1))

    def this_week(self):
        return self.filter(start_date__year=self.current_date.year, start_date__week=self.current_isodate.week)

    def next_week(self):
        next_week = (self.current_date + relativedelta(weeks=1)).isocalendar()
        return self.filter(start_date__year=next_week.year, start_date__week=next_week.week)

    def this_month(self):
        return self.filter(start_date__year=self.current_date.year, start_date__month=self.current_date.month)

    def next_month(self):
        next_month = self.current_date + relativedelta(months=1)
        return self.filter(start_date__year=next_month.year, start_date__month=next_month.month)


class EventManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(live__isnull=True)
            .exclude(end_date__lt=timezone.now())
            .order_by('start_date')
        )
