from datetime import datetime

from django.db.models import Q
from django_filters import CharFilter, FilterSet
from wagtail.core.models import Page


class PageFilter(FilterSet):

    after = CharFilter(method='filter_time_id')

    def filter_time_id(self, queryset, name, value):
        value = value or '0.000000_0'
        after_ts_str, after_id_str = value.split('_')
        after_ts = datetime.fromtimestamp(float(after_ts_str))
        after_id = int(after_id_str)

        return queryset.filter(Q(last_published_at=after_ts, id__gt=after_id) | Q(last_published_at__gt=after_ts))

    class Meta:
        model = Page
        fields = ['after']
