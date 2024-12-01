from rest_framework import serializers

from corelab.models import Patients

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = ('patient_id', 'name', 'gender', 'dob')