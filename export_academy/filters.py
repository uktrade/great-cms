from django.db.models import Q
from django.utils import timezone
from django_filters import FilterSet, filters
from great_components import forms

from export_academy import models
from export_academy.helpers import is_export_academy_registered


class EventFilter(FilterSet):
    ALL = 'all'

    TODAY = 'today'
    TOMORROW = 'tomorrow'
    THIS_WEEK = 'this_week'
    NEXT_WEEK = 'next_week'
    THIS_MONTH = 'this_month'
    NEXT_MONTH = 'next_month'

    PERIOD_CHOICES = [
        [ALL, 'All'],
        [TODAY, 'Today'],
        [TOMORROW, 'Tomorrow'],
        [THIS_WEEK, 'This Week'],
        [NEXT_WEEK, 'Next Week'],
        [THIS_MONTH, 'This Month'],
        [NEXT_MONTH, 'Next Month'],
    ]

    UPCOMING = 'upcoming'
    PAST = 'past'

    BOOKING_PERIOD_CHOICES = [
        [ALL, 'All'],
        [UPCOMING, 'Current bookings'],
        [PAST, 'Past bookings'],
    ]

    type = filters.ModelMultipleChoiceFilter(
        label='Content',
        field_name='types__slug',
        queryset=models.EventTypeTag.objects.all(),
        to_field_name='slug',
        widget=forms.CheckboxSelectInlineLabelMultiple,
    )

    format = filters.MultipleChoiceFilter(
        label='Format',
        choices=models.Event.FORMAT_CHOICES,
        widget=forms.CheckboxSelectInlineLabelMultiple,
    )

    period = filters.ChoiceFilter(
        label='Date',
        empty_label=None,
        choices=PERIOD_CHOICES,
        method='filter_period',
        widget=forms.RadioSelect,
    )

    booking_period = filters.ChoiceFilter(
        label='Events',
        empty_label=None,
        choices=BOOKING_PERIOD_CHOICES,
        method='filter_booking_period',
        widget=forms.RadioSelect,
    )

    class Meta:
        model = models.Event
        fields = ['booking_period', 'type', 'format', 'period']

    def filter_period(self, queryset, _name, value):
        for param, _ in self.PERIOD_CHOICES:
            # there must be a matching method for 'period' choices in the queryset manager (./managers.py)
            if param in value:
                if hasattr(queryset, '%s' % param):
                    queryset = getattr(queryset, '%s' % param)()

        return queryset

    def filter_booking_period(self, queryset, _name, value):
        if is_export_academy_registered(self.request.user):  # type: ignore
            if value == self.UPCOMING:
                queryset = queryset.exclude(live__isnull=True).filter(
                    Q(
                        bookings__registration__email=self.request.user.email,  # type: ignore
                        bookings__status=models.Booking.CONFIRMED,
                    )
                    | Q(
                        bookings__registration__email=self.request.user.email,  # type: ignore
                        bookings__status=models.Booking.JOINED,
                    )
                )

            if value == self.PAST:
                queryset = self.Meta.model.objects.exclude(live__isnull=True).filter(
                    bookings__registration__email=self.request.user.email, end_date__lt=timezone.now()  # type: ignore
                )
        elif value == self.ALL:
            queryset = queryset
        else:
            queryset = queryset.none()

        return queryset
