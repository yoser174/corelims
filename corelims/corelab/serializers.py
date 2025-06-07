from .models import (
    Orders,
    OrderResults,
    Priority,
    Origins,
    Doctors,
    Patients,
    Insurance,
    Instruments,
)
from rest_framework import serializers


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
    """
    InsuranceSerializer
    Serializer for the Insurance model.
    This serializer includes all fields from the Insurance model.
    It is used to serialize and deserialize Insurance instances.
    It can be used in API views to handle Insurance data.
    It can also be used in forms to handle Insurance data.
    It can be used in Django admin to handle Insurance data.
    It can be used in Django views to handle Insurance data.
    It can be used in Django templates to handle Insurance data.
    It can be used in Django signals to handle Insurance data.
    It can be used in Django management commands to handle Insurance data.
    It can be used in Django custom management commands to handle Insurance data.
    It can be used in Django custom commands to handle Insurance data.
    It can be used in Django custom serializers to handle Insurance data.
    It can be used in Django custom views to handle Insurance data.
    It can be used in Django custom forms to handle Insurance data.

    Args:
        serializers (_type_): _description_
    """

    class Meta:
        model = Insurance
        fields = "__all__"


class DoctorsSerializer(serializers.ModelSerializer):
    """
    DoctorsSerializer
    Serializer for the Doctors model.
    This serializer includes all fields from the Doctors model.
    It is used to serialize and deserialize Doctors instances.
    It can be used in API views to handle Doctors data.

    Args:
        serializers (_type_): _description_
    """

    class Meta:
        """
        Meta class for DoctorsSerializer
        This class defines the model and fields for the DoctorsSerializer.
        It specifies that the serializer is for the Doctors model and includes all fields.
        It can be used in API views to handle Doctors data.
        It can also be used in forms to handle Doctors data.
        It can be used in Django admin to handle Doctors data.
        It can be used in Django views to handle Doctors data.
        It can be used in Django templates to handle Doctors data.
        It can be used in Django signals to handle Doctors data.
        It can be used in Django management commands to handle Doctors data.
        It can be used in Django custom management commands to handle Doctors data.
        """

        model = Doctors
        fields = "__all__"


class ResultsSerializer(serializers.ModelSerializer):
    """
    ResultsSerializer
    Serializer for the OrderResults model.
    This serializer includes all fields from the OrderResults model.
    It is used to serialize and deserialize OrderResults instances.
    It can be used in API views to handle OrderResults data.
    It can also be used in forms to handle OrderResults data.
    It can be used in Django admin to handle OrderResults data.
    It can be used in Django views to handle OrderResults data.
    It can be used in Django templates to handle OrderResults data.
    It can be used in Django signals to handle OrderResults data.
    It can be used in Django management commands to handle OrderResults data.
    It can be used in Django custom management commands to handle OrderResults data.
    It can be used in Django custom commands to handle OrderResults data.
    """

    class Meta:
        """
        Meta class for ResultsSerializer
        This class defines the model and fields for the ResultsSerializer.
        It specifies that the serializer is for the OrderResults model and includes all fields.
        """

        model = OrderResults
        fields = "__all__"


class InstrumentsSerializer(serializers.ModelSerializer):
    """
    InstrumentsSerializer
    Serializer for the Instruments model.
    """

    class Meta:
        """
        Meta class for InstrumentsSerializer
        This class defines the model and fields for the InstrumentsSerializer.
        It specifies that the serializer is for the Instruments model and includes all fields.
        """

        model = Instruments
        fields = "__all__"
