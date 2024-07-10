import datetime

from django.db.models import Q
from django_filters import CharFilter, FilterSet
from wagtail.models import Page


class PageFilter(FilterSet):
    after = CharFilter(method='filter_time_id')

    def filter_time_id(self, queryset, name, value):
        value = value or '0.000000_0'
        after_ts_str, after_id_str = value.split('_')
        after_ts = datetime.datetime.fromtimestamp(float(after_ts_str))
        after_id = int(after_id_str)

        return queryset.filter(Q(last_published_at=after_ts, id__gt=after_id) | Q(last_published_at__gt=after_ts))

    class Meta:
        model = Page
        fields = ['after']


class ActivityStreamExportAcademyFilter(FilterSet):
    after = CharFilter(method='filter_after')

    def filter_after(self, queryset, name, value):
        value = value or '0.000000'
        after_ts = datetime.datetime.fromtimestamp(float(value), tz=datetime.timezone.utc)
        return queryset.filter(modified__gt=after_ts)


class ActivityStreamExpandYourBusinessFilter(FilterSet):
    after = CharFilter(method='filter_after')

    def filter_after(self, queryset, name, value):
        value = value or '0'
        return queryset.filter(id__gt=value)


class ActivityStreamCmsContentFilter(FilterSet):
    after = CharFilter(method='filter_after')

    def filter_after(self, queryset, name, value):
        value = value or '0'
        return queryset.filter(id__gt=value)


class ActivityStreamWhereToExportFilter(FilterSet):
    after = CharFilter(method='filter_after')

    def filter_after(self, queryset, name, value):
        value = value or '0'
        return queryset.filter(id__gt=value)
