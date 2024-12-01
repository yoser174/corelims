from django.shortcuts import render
from rest_framework import viewsets

from corelab.models import Patients
from .serializers import TodoSerializer

# Create your views here.

class PatientsView(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    queryset = Patients.objects.all()