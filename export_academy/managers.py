import datetime

from django.db import models


class EventQuerySet(models.QuerySet):
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()
    current_isodate = current_date.isocalendar()

    def all(self):
        return self

    def today(self):
        return self.filter(start_date__date=self.current_date)

    def tomorrow(self):
        return self.filter(start_date__date=self.current_date + datetime.timedelta(days=1))

    def this_week(self):
        return self.filter(start_date__year=self.current_isodate.year, start_date__week=self.current_isodate.week)

    def next_week(self):
        return self.filter(start_date__year=self.current_isodate.year, start_date__week=self.current_isodate.week + 1)

    def this_month(self):
        return self.filter(start_date__year=self.current_date.year, start_date__month=self.current_date.month)

    def next_month(self):
        return self.filter(
            start_date__year__gte=self.current_date.year, start_date__month__gte=self.current_date.month + 1
        )
