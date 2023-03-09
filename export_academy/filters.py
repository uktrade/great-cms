from django_filters import FilterSet, filters
from great_components import forms

from export_academy import models


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

    type = filters.ModelMultipleChoiceFilter(
        label='type',
        field_name='types__slug',
        queryset=models.EventTypeTag.objects.all(),
        to_field_name='slug',
        widget=forms.CheckboxSelectInlineLabelMultiple,
    )

    format = filters.MultipleChoiceFilter(
        label='format',
        choices=models.Event.FORMAT_CHOICES,
        widget=forms.CheckboxSelectInlineLabelMultiple,
    )

    period = filters.ChoiceFilter(
        label='period',
        empty_label=None,
        choices=PERIOD_CHOICES,
        method='filter_period',
        widget=forms.RadioSelect,
    )

    class Meta:
        model = models.Event
        fields = ['type', 'format', 'period']

    def filter_period(self, queryset, _name, value):
        for param, _ in self.PERIOD_CHOICES:
            # there must be a matching method for 'period' choices in the queryset manager (./managers.py)
            if param in value:
                queryset = getattr(queryset, '%s' % param)()

        return queryset
