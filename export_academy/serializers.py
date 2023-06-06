from rest_framework import serializers

from export_academy.models import Booking, Registration


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def to_representation(self, obj):
        return {
            "id": str(obj.id),
            "event_id": str(obj.event.id),
            "registration_id": obj.registration.email,
            "status": obj.status,
        }


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'
