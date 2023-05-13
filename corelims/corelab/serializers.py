from django.contrib.auth.models import User, Group
from .models import (
    Orders,
    OrderTests,
    OrderSamples,
    OrderResults,
    Priority,
    Origins,
    Doctors,
    Patients,
    Insurance,
)
from rest_framework import serializers
from django.forms.models import model_to_dict


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = "__all__"


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = "__all__"


class PatientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = "__all__"


class OriginsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origins
        fields = "__all__"


class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = "__all__"


class DoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctors
        fields = "__all__"


class ResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderResults
        fields = "__all__"


"""   
class OrderSamplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderResults
        fields = '__all__'

class OrderResultsSerializer(serializers.ModelSerializer):
    #samples = OrderSamplesSerializer(many=True, read_only=True)
    #doctor_name = serializers.SerializerMethodField('get_doctor')
    
    #orderresults_order = serializers.RelatedField(read_only=True)
    
    priority_name = serializers.CharField(source='priority.name', read_only=True)
    origin_name = serializers.CharField(source='origin.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    
    orderresults_order = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-order-result'
    )
    
    class Meta:
        model = Orders
        fields = ('order_date','number','patient_id','patient_name','priority_name','origin_name','doctor_name','orderresults_order')

        

    


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
"""
