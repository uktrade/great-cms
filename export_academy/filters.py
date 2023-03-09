from django_filters import FilterSet, filters

from export_academy import models


class EventFilter(FilterSet):
    ALL = 'all'
    TODAY = 'today'
    TOMORROW = 'tomorrow'
    THIS_WEEK = 'this_week'
    NEXT_WEEK = 'next_week'
    THIS_MONTH = 'this_month'
    NEXT_MONTH = 'next_month'

    WHEN_CHOICES = [
        [ALL, 'All'],
        [TODAY, 'Today'],
        [TOMORROW, 'Tomorrow'],
        [THIS_WEEK, 'This Week'],
        [NEXT_WEEK, 'Next Week'],
        [THIS_MONTH, 'This Month'],
        [NEXT_MONTH, 'Next Month'],
    ]

    when = filters.ChoiceFilter(
        choices=WHEN_CHOICES,
        method='filter_when',
    )

    format = filters.MultipleChoiceFilter(
        choices=models.Event.FORMAT_CHOICES,
    )

    class Meta:
        model = models.Event
        fields = ['when', 'format']

    def filter_when(self, queryset, name, value):
        for param, _ in self.WHEN_CHOICES:
            # there must be a matching method for 'when' choices in the queryset manager (./managers.py)
            if param in value:
                queryset = getattr(queryset, '%s' % param)()

        return queryset
