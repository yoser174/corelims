import django_filters
import datetime
from .models import TestGroups,Tests,Orders,Patients,HistoryOrders,OrderTests

class TestGroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = TestGroups
        fields = ['name']

class TestFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Tests
        fields = ['test_group','name']
        
class OrderFilter(django_filters.FilterSet):
    order_date = django_filters.DateRangeFilter()
    number = django_filters.CharFilter(lookup_expr='icontains')
    #sample_order__sample_no = django_filters.CharFilter(lookup_expr='icontains')
    patient__patient_id = django_filters.CharFilter(lookup_expr='icontains')
    patient__name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Orders
        fields = ['order_date','origin','number','patient__patient_id','patient__name']
        
class PatientFilter(django_filters.FilterSet):
    patient_id = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    address = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Patients
        fields = ['patient_id','name','address']

class JMFilter(django_filters.FilterSet):
    class Meta:
        model = Orders
        fields = ['order_date']
        
class inpatmedsrvFilter(django_filters.FilterSet):
    patient__patient_id = django_filters.CharFilter(lookup_expr='icontains')
    patient__name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Orders
        fields = ['patient__patient_id','patient__name']
        
class InsuranceFilter(django_filters.FilterSet):
    class Meta:
        model = Orders
        fields = ['order_date']

class OriginFilter(django_filters.FilterSet):
    class Meta:
        model = Orders
        fields = ['order_date']

class TestsFilter(django_filters.FilterSet):
    class Meta:
        model = Orders
        fields = ['order_date']

class OrderFilter(django_filters.FilterSet):
    order_date = django_filters.DateRangeFilter() 
    number = django_filters.CharFilter(lookup_expr='icontains')
    patient__patient_id = django_filters.CharFilter(lookup_expr='icontains')
    patient__name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Orders
        fields = ['order_date','service','origin','insurance','number','patient__patient_id','patient__name']


class WokareaFilter(django_filters.FilterSet):
    order_date = django_filters.DateRangeFilter() 
    number = django_filters.CharFilter(lookup_expr='icontains')
    patient__patient_id = django_filters.CharFilter(lookup_expr='icontains')
    patient__name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Orders
        fields = ['order_date','service','origin','insurance','number','patient__patient_id','patient__name','status']        
        
class OrderHistoryFilter(django_filters.FilterSet):
    class Meta:
        model = HistoryOrders
        fields = ['test','action_user','action_code','action_text']
        
class WorklistFilter(django_filters.FilterSet):
    order_date = django_filters.DateRangeFilter()
    number = django_filters.CharFilter(lookup_expr='icontains')
    patient__patient_id = django_filters.CharFilter(lookup_expr='icontains')
    patient__name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Orders
        fields = ['order_date','number','patient__patient_id','patient__name']
        
class PatTransHistFilter(django_filters.FilterSet):
    class Meta:
        model = OrderTests
        fields = ['order__order_date']