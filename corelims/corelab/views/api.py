from rest_framework import generics, viewsets

from corelab import models
from corelab.serializers import (
    DoctorsSerializer,
    InstrumentsSerializer,
    InsuranceSerializer,
    OrdersSerializer,
    OriginsSerializer,
    PatientsSerializer,
    ResultsSerializer,
)


class OrderListViewSet(generics.ListAPIView):
    queryset = models.Orders.objects.all()
    serializer_class = OrdersSerializer
    # filter_backends = (resfilters.SearchFilter,)
    search_fields = (
        "id",
        "number",
        "order_date",
    )


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Orders.objects.all()
    serializer_class = OrdersSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = models.Patients.objects.all()
    serializer_class = PatientsSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = models.Doctors.objects.all()
    serializer_class = DoctorsSerializer


class OriginViewSet(viewsets.ModelViewSet):
    queryset = models.Origins.objects.all()
    serializer_class = OriginsSerializer


class InsuranceViewSet(viewsets.ModelViewSet):
    queryset = models.Insurance.objects.all()
    serializer_class = InsuranceSerializer


class ResultViewSet(viewsets.ModelViewSet):
    queryset = models.OrderResults.objects.all()
    serializer_class = ResultsSerializer


class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = models.Instruments.objects.all()
    serializer_class = InstrumentsSerializer
