from rest_framework import generics, viewsets

from corelab import models
from corelab.serializers import (
    DoctorsSerializer,
    HistoryOrdersSerializer,
    InstrumentTestsSerializer,
    InstrumentsSerializer,
    InsuranceSerializer,
    OrderSamplesSerializer,
    OrdersSerializer,
    OriginsSerializer,
    PatientsSerializer,
    ResultsSerializer,
    OrderResultsSerializer,
    TestsSerializer,
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
    queryset = models.Results.objects.all()
    serializer_class = ResultsSerializer


class InstrumentViewSet(viewsets.ModelViewSet):
    """InstrumentViewSet
    ViewSet for managing instruments.
    This viewset provides CRUD operations for instruments.
    It allows filtering by instrument ID through query parameters.
    """

    queryset = models.Instruments.objects.all()
    serializer_class = InstrumentsSerializer

    def get_queryset(self):
        """Get the queryset for the InstrumentViewSet.
        This method overrides the default get_queryset method to filter
        the queryset based on the 'id' query parameter.
        Returns:
            queryset: Filtered queryset based on the provided 'id' query parameter.
        """
        queryset = super().get_queryset()
        instrument_id = self.request.query_params.get("id", None)
        if instrument_id is not None:
            queryset = queryset.filter(id=instrument_id)
        return queryset


class OrderSamplesViewSet(viewsets.ModelViewSet):
    queryset = models.OrderSamples.objects.all()
    serializer_class = OrderSamplesSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sample_no = self.request.query_params.get("sample_no", None)
        print(sample_no)
        if sample_no is not None:
            queryset = queryset.filter(sample_no=sample_no)
        return queryset


class InstrumentTestsViewSet(viewsets.ModelViewSet):
    queryset = models.InstrumentTests.objects.all()
    serializer_class = InstrumentTestsSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        instrument_id = self.request.query_params.get("instrument_id", None)
        test_code = self.request.query_params.get("test_code", None)
        if instrument_id is not None and test_code is not None:
            queryset = queryset.filter(instrument_id=instrument_id, test_code=test_code)
        return queryset


class OrderResultsViewSet(viewsets.ModelViewSet):
    """OrderResultsViewSet
    ViewSet for managing order results.
    This viewset provides CRUD operations for order results.
    It allows filtering by order_id and test_id through query parameters.
    """

    queryset = models.OrderResults.objects.all()
    serializer_class = OrderResultsSerializer

    def get_queryset(self):
        """Get the queryset for the OrderResultsViewSet.
        This method overrides the default get_queryset method to filter
        the queryset based on query parameters 'order_id' and 'test_id'.
        Returns:
            queryset: Filtered queryset based on the provided query parameters.
        """
        # Get the base queryset from the parent class
        queryset = super().get_queryset()
        order_id = self.request.query_params.get("order_id", None)
        test_id = self.request.query_params.get("test_id", None)
        if order_id is not None and test_id is not None:
            queryset = queryset.filter(order_id=order_id, test_id=test_id)
        return queryset


class HistoryOrdersViewSet(viewsets.ModelViewSet):
    """HistoryOrdersViewSet
    ViewSet for managing historical orders.
    This viewset provides CRUD operations for historical orders.
    It allows filtering by order_id and test_id through query parameters.
    """

    queryset = models.HistoryOrders.objects.all()
    serializer_class = HistoryOrdersSerializer

    def get_queryset(self):
        """Get the queryset for the HistoryOrdersViewSet.
        This method overrides the default get_queryset method to filter
        the queryset based on query parameters 'order_id' and 'test_id'.
        Returns:
            queryset: Filtered queryset based on the provided query parameters.
        """
        queryset = super().get_queryset()
        order_id = self.request.query_params.get("order_id", None)
        test_id = self.request.query_params.get("test_id", None)
        if order_id is not None and test_id is not None:
            queryset = queryset.filter(order_id=order_id, test_id=test_id)
        return queryset


class TestsViewSet(viewsets.ModelViewSet):
    """TestViewSet
    ViewSet for managing tests.
    This viewset provides CRUD operations for tests.
    """

    queryset = models.Tests.objects.all()
    serializer_class = TestsSerializer
    """ This method overrides the default get_queryset method to filter
    the queryset based on the 'id' query parameter.
    Returns:
        queryset: Filtered queryset based on the provided 'id' query parameter.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        test_id = self.request.query_params.get("id", None)
        if test_id is not None:
            queryset = queryset.filter(id=test_id)
        return queryset


#     serializer_class = TestsSerializer
