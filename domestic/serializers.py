from django.core.serializers.python import Serializer


class MarketGuidesMapSerializer(Serializer):
    def end_object(self, obj):
        self._current['latlng'] = obj.country.latlng
        self._current['url'] = f'/markets/{obj.slug}/'
        self._current['tags'] = list(obj.tags.all().values_list('name', flat=True))
        self.objects.append(self._current)
