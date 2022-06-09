from django.core.serializers.python import Serializer


class MarketGuidesMapSerializer(Serializer):
    def end_object(self, obj):
        self._current['country__latlng'] = obj.country.latlng
        self.objects.append(self._current)
