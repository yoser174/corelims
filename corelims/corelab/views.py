from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils.translation import activate
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import models, tables, forms, filters, query, report
from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from django_tables2 import SingleTableView, RequestConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count
from .tables import (
    TestGroupsTable,
    PatientsTable,
    SelectPatientsTable,
    JMTable,
    InsuranceTable,
    TestsTable,
    OriginTable,
    WorklistTable,
    InpatMedSrvTable,
    TransTable,
    InstrumentBachModeTable,
)
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from extra_views.advanced import (
    UpdateWithInlinesView,
    NamedFormsetsMixin,
    CreateWithInlinesView,
    InlineFormSet,
    ModelFormMixin,
)
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from .custom.mixins import (
    UpdateWithInlinesAndModifiedByMixin,
    CreateWithInlinesAndModifiedByMixin,
)
from avatar.forms import PrimaryAvatarForm, UploadAvatarForm
from avatar.views import _get_avatars
from avatar.models import Avatar
from avatar.signals import avatar_updated
from avatar.utils import invalidate_cache
import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.dateformat import DateFormat
from django_tables2.config import RequestConfig
from django_tables2.export.export import TableExport
import serial, time

from datetime import datetime, timedelta, time
from pyreportjasper import JasperPy

from .utils import is_float
from .labels import Label
from corelab.templatetags import wa_status


## language all
from django.utils import translation

user_language = "id"
translation.activate(user_language)
# request.session[translation.LANGUAGE_SESSION_KEY] = user_language

import django_filters.rest_framework

from django.contrib.auth.models import User, Group
from rest_framework import generics, viewsets
from rest_framework import filters as resfilters
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import (
    OrdersSerializer,
    PatientsSerializer,
    OriginsSerializer,
    DoctorsSerializer,
    ResultsSerializer,
    InsuranceSerializer,
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK


UPDATE = """

"""
settings.UPDATE = UPDATE


# ######################
# ##   Helper Views   ##
# ######################
@login_required(login_url="login_billing")
class UpdateUserProfile(LoginRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "auth/user_form_billing.html"
    success_url = reverse_lazy("home_billing")


def login_user(request):
    logout(request)
    next_url = request.GET.get("next", "")
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language

    if request.POST:
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        next_url = request.POST.get("next", "")

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if next_url != "":
                    return HttpResponseRedirect(next_url)
                else:
                    return redirect(reverse_lazy("dashboard_billing"), permanent=True)
        else:
            messages.error(request, _("Wrong username and/or password."))

    context = {"next": next_url}
    return render(request, "registration/login_billing.html", context)


@login_required(login_url="login_billing")
def show_dashboard(request):
    today = timezone.now().date()
    ordercount_today = models.Orders.objects.filter(order_date__gte=today).count()
    patientcount_today = models.Patients.objects.filter(
        dateofcreation__gte=today
    ).count()
    context = {
        "ordercount_today": ordercount_today,
        "patientcount_today": patientcount_today,
    }
    next_url = request.GET.get("next")
    if next_url:
        return HttpResponseRedirect(next_url)
    else:
        return render(request, "dashboard_billing.html", context)


@login_required(login_url="login_billing")
def AvatarChange(
    request,
    extra_context=None,
    next_override=None,
    upload_form=UploadAvatarForm,
    primary_form=PrimaryAvatarForm,
    *args,
    **kwargs
):
    if extra_context is None:
        extra_context = {}

    avatar, avatars = _get_avatars(request.user)
    if avatar:
        kwargs = {"initial": {"choice": avatar.id}}
    else:
        kwargs = {}
    upload_avatar_form = upload_form(user=request.user, **kwargs)
    primary_avatar_form = primary_form(
        request.POST or None, user=request.user, avatars=avatars, **kwargs
    )

    if request.method == "POST":
        updated = False
        if "choice" in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(id=primary_avatar_form.cleaned_data["choice"])
            avatar.primary = True
            avatar.save()
            updated = True
            invalidate_cache(request.user)
            messages.success(request, _("Successfully updated your avatar."))
        if updated:
            avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
        return render(request, "auth/avatar_change_billing.html")

    context = {
        "avatar": avatar,
        "avatars": avatars,
        "upload_avatar_form": upload_avatar_form,
        "primary_avatar_form": primary_avatar_form,
        "next": next_override,
    }
    context.update(extra_context)
    template_name = "auth/avatar_change_billing.html"
    return render(request, template_name, context)


@login_required(login_url="login_billing")
def AvatarAdd(
    request,
    extra_context=None,
    next_override=None,
    upload_form=UploadAvatarForm,
    *args,
    **kwargs
):
    if extra_context is None:
        extra_context = {}
    avatar, avatars = _get_avatars(request.user)
    upload_avatar_form = upload_form(
        request.POST or None, request.FILES or None, user=request.user
    )
    if request.method == "POST" and "avatar" in request.FILES:
        if upload_avatar_form.is_valid():
            avatar = Avatar(user=request.user, primary=True)
            image_file = request.FILES["avatar"]
            avatar.avatar.save(image_file.name, image_file)
            avatar.save()
            invalidate_cache(request.user)
            messages.success(request, _("Successfully uploaded a new avatar."))
            avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
            return render(request, "auth/avatar_change_billing.html")
    context = {
        "avatar": avatar,
        "avatars": avatars,
        "upload_avatar_form": upload_avatar_form,
        "next": next_override,
    }
    context.update(extra_context)
    template_name = "auth/avatar_add_billing.html"
    return render(request, template_name, context)


@login_required(login_url="login_billing")
def patient_print_bill(request, pk):
    origin_id = request.GET.get("origin_id")
    insurance_id = request.GET.get("insurance_id")
    # print origin_id
    # print insurance_id
    origin = None
    insurance = None
    patient = models.Patients.objects.get(pk=pk)
    filter_sql = " "

    if insurance_id != "None":
        insurance = models.Insurance.objects.get(pk=insurance_id)
        filter_sql += " AND insurance_id = '" + insurance_id + "' "

    if origin_id != "None":
        origin = models.Origins.objects.get(pk=origin_id)
        filter_sql += " AND origin_id = '" + origin_id + "' "

    detail = query.medical_service_dtl(pk, filter_sql)
    total = query.medical_service_dtl_total(pk, filter_sql)

    org_lab_name = models.Parameters.objects.filter(name="ORG_LAB_NAME")
    org_lab_address = models.Parameters.objects.filter(name="ORG_LAB_ADDRESS")
    org_lab_city = models.Parameters.objects.filter(name="ORG_LAB_CITY")

    template = "corelab/patient_print_bill.html"
    context = {
        "date": timezone.now().date(),
        "origin": origin,
        "insurance": insurance,
        "patient": patient,
        "detail": detail,
        "total": total,
    }
    return render(request, template, context)


@login_required(login_url="login_billing")
def patient_trans_history(request, pk):
    data = models.OrderTests.objects.filter(order__patient_id=pk)
    today = timezone.now().date()

    if request.GET.get("order__order_date"):
        d_range = request.GET.get("order__order_date")
        start_date = d_range[:10]
        end_date = d_range[13:23]
    else:
        start_date = today
        end_date = today

    data = data.filter(order__order_date__range=[start_date, end_date])

    filter = filters.PatTransHistFilter(request.GET, queryset=data)
    patient = models.Patients.objects.get(pk=pk)

    transtable = TransTable(data)
    transtable.paginate(page=request.GET.get("page", 1), per_page=10)

    template = "corelab/patient_trans_history.html"

    context = {"patient": patient, "transtable": transtable, "filter": filter}
    return render(request, template, context)


@login_required(login_url="login_billing")
def patient_trans_history_perview(request, pk):
    template = "report/orders.html"
    data = models.OrderTests.objects.filter(order__patient_id=pk)
    today = timezone.now().date()

    output = "pdf"

    # if request.GET.get('export'):
    #    output = request.GET.get('export')

    if request.GET.get("order__order_date") == "None":
        start_date = "2000-01-01"
        end_date = "3000-12-31"
    elif request.GET.get("order__order_date"):
        d_range = request.GET.get("order__order_date")
        start_date = d_range[:10]
        end_date = d_range[13:23]
    else:
        start_date = today
        end_date = today

    data = data.filter(order__order_date__range=[start_date, end_date])
    filter = filters.PatTransHistFilter(request.GET, queryset=data)
    res_rep = report.JasperServer()
    b_ok, content = res_rep.get_patient_trans_history(
        start_date, end_date, output, patient_id=pk
    )
    if b_ok:
        response = HttpResponse(content, content_type="application/pdf")
    else:
        response = JsonResponse(content)

    return response


# #################################
# ##         Report Views        ##
# #################################
@login_required(login_url="login_billing")
def report_tests(request):
    template = "report/insurance.html"
    data = (
        models.Orders.objects.values("order_items__test__name")
        .annotate(Count("number"))
        .order_by()
    )

    if request.GET.get("order_date"):
        d_range = request.GET.get("order_date")
        # 04/01/2018 - 04/30/2018
        start_date = d_range[:10]
        end_date = d_range[13:23]

        data = data.filter(order_date__range=[start_date, end_date])

    filter = filters.TestsFilter(request.GET, queryset=data)
    orderstable = TestsTable(data)
    orderstable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(orderstable)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, orderstable)
        return exporter.response("table.{}".format(export_format))

    context = {"orderstable": orderstable, "filter": filter}
    return render(request, template, context)


@login_required(login_url="login_billing")
def report_insurance(request):
    template = "report/insurance.html"
    data = (
        models.Orders.objects.values("insurance__name")
        .annotate(Count("number"))
        .order_by()
    )

    if request.GET.get("order_date"):
        d_range = request.GET.get("order_date")
        # 04/01/2018 - 04/30/2018
        start_date = d_range[:10]
        end_date = d_range[13:23]

        data = data.filter(order_date__range=[start_date, end_date])

    filter = filters.InsuranceFilter(request.GET, queryset=data)
    orderstable = InsuranceTable(data)
    orderstable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(orderstable)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, orderstable)
        return exporter.response("table.{}".format(export_format))

    context = {"orderstable": orderstable, "filter": filter}
    return render(request, template, context)


@login_required(login_url="login_billing")
def report_origin(request):
    template = "report/origin.html"
    data = (
        models.Orders.objects.values("origin__name")
        .annotate(Count("number"))
        .order_by()
    )

    if request.GET.get("order_date"):
        d_range = request.GET.get("order_date")
        # 04/01/2018 - 04/30/2018
        start_date = d_range[:10]
        end_date = d_range[13:23]

        data = data.filter(order_date__range=[start_date, end_date])

    filter = filters.OriginFilter(request.GET, queryset=data)
    orderstable = OriginTable(data)
    orderstable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(orderstable)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, orderstable)
        return exporter.response("table.{}".format(export_format))

    context = {"orderstable": orderstable, "filter": filter}
    return render(request, template, context)


@login_required(login_url="login_billing")
def report_inpatmedsrv(request):
    template = "report/inpatmedsrv.html"
    inpat = models.Service.objects.get(pk=1)

    data = (
        models.Orders.objects.filter(service=inpat)
        .values(
            "patient__patient_id", "patient__name", "origin__name", "insurance__name"
        )
        .annotate(dcount=Count("patient__patient_id"))
        .exclude(patient__patient_id__isnull=True)
        .all()
    )
    # .order_by('patient__name')

    filter = filters.inpatmedsrvFilter(request.GET, queryset=data)
    orderstable = InpatMedSrvTable(filter)
    orderstable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(orderstable)

    context = {"orderstable": orderstable, "filter": filter}
    return render(request, template, context)


@login_required(login_url="login_billing")
def report_orders(request):
    template = "report/orders.html"
    data = models.Orders.objects.all()
    today = timezone.now().date()

    output = "html"

    if request.GET.get("export"):
        output = request.GET.get("export")

    if request.GET.get("order_date"):
        d_range = request.GET.get("order_date")
        start_date = d_range[:10]
        end_date = d_range[13:23]
    else:
        start_date = today
        end_date = today

    data = data.filter(order_date__range=[start_date, end_date])

    filter = filters.JMFilter(request.GET, queryset=data)

    report_content = ""

    res_rep = report.JasperServer()

    b_ok, content = res_rep.get_report_orders(start_date, end_date, output)

    report_content = content

    response = ""

    if output != "html":
        if output == "xlsx":
            response = HttpResponse(
                content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        if output == "pdf":
            response = HttpResponse(content, content_type="application/pdf")
        if output == "docx":
            response = HttpResponse(
                content,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        return response

    context = {"report": report_content, "filter": filter}
    return render(request, template, context)

@login_required(login_url="login_billing")
def report_ordertests(request):
    template = "report/ordertests.html"
    data = models.Orders.objects.all()
    today = timezone.now().date()

    output = "html"

    if request.GET.get("export"):
        output = request.GET.get("export")

    if request.GET.get("order_date"):
        d_range = request.GET.get("order_date")
        start_date = d_range[:10]
        end_date = d_range[13:23]
    else:
        start_date = today
        end_date = today

    data = data.filter(order_date__range=[start_date, end_date])

    filter = filters.JMFilter(request.GET, queryset=data)

    report_content = ""

    res_rep = report.JasperServer()

    b_ok, content = res_rep.get_report_ordertests(start_date, end_date, output)

    report_content = content

    response = ""

    if output != "html":
        if output == "xlsx":
            response = HttpResponse(
                content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        if output == "pdf":
            response = HttpResponse(content, content_type="application/pdf")
        if output == "docx":
            response = HttpResponse(
                content,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        return response

    context = {"report": report_content, "filter": filter}
    return render(request, template, context)

@login_required(login_url="login_billing")
def report_tats(request):
    template = "report/tats.html"
    data = models.Orders.objects.all()
    today = timezone.now().date()

    output = "html"

    if request.GET.get("export"):
        output = request.GET.get("export")

    if request.GET.get("order_date"):
        d_range = request.GET.get("order_date")
        start_date = d_range[:10]
        end_date = d_range[13:23]
    else:
        start_date = today
        end_date = today

    data = data.filter(order_date__range=[start_date, end_date])

    filter = filters.JMFilter(request.GET, queryset=data)

    report_content = ""

    res_rep = report.JasperServer()

    b_ok, content = res_rep.get_report_tats(start_date, end_date, output)

    if not b_ok:
        return JsonResponse(content)

    report_content = content

    response = ""

    if output != "html":
        if output == "xlsx":
            response = HttpResponse(
                content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        if output == "pdf":
            response = HttpResponse(content, content_type="application/pdf")
        if output == "docx":
            response = HttpResponse(
                content,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        return response

    context = {"report": report_content, "filter": filter}
    return render(request, template, context)


@login_required(login_url="login_billing")
def report_jm(request):
    template = "report/jm.html"
    data = models.Orders.objects.all()
    today = timezone.now().date()

    if request.GET.get("order_date"):
        d_range = request.GET.get("order_date")
        start_date = d_range[:10]
        end_date = d_range[13:23]
    else:
        start_date = today
        end_date = today

    data = data.filter(order_date__range=[start_date, end_date])

    filter = filters.JMFilter(request.GET, queryset=data)
    orderstable = JMTable(data)
    orderstable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(orderstable)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, orderstable)
        return exporter.response("table.{}".format(export_format))

    context = {"orderstable": orderstable, "filter": filter}
    return render(request, template, context)


# #################################
# ##   Billing Function Views  ##
# #################################
@login_required(login_url="login_billing")
def home(request):
    template = "index_billing.html"
    workareas = models.Workarea.objects.all().order_by("sort")
    org_lab_name = models.Parameters.objects.filter(name="ORG_LAB_NAME")
    org_lab_address = models.Parameters.objects.filter(name="ORG_LAB_ADDRESS")
    update = settings.UPDATE
    context = {
        "workareas": workareas,
        "org_lab_name": org_lab_name,
        "org_lab_address": org_lab_address,
        "version": settings.VERSION,
        "update": update,
    }
    return render(request, template, context)


@login_required(login_url="login_billing")
def order_patient(request):
    workareas = models.Workarea.objects.all().order_by("sort")
    if request.method == "POST":
        patient_pk = request.POST.get("patient", "")
        return redirect("create_order_from_patient", patient_pk=patient_pk)
    else:
        template = "select/select_patient.html"
        patients = models.Patients.objects.all()
        data = models.Patients.objects.all()
        if request.GET.get("patient_id"):
            data = data.filter(patient_id__contains=request.GET.get("patient_id"))
        if request.GET.get("name"):
            data = data.filter(name__contains=request.GET.get("name"))

        filter = filters.PatientFilter(request.GET, queryset=patients)
        patienttable = SelectPatientsTable(data)
        patienttable.paginate(page=request.GET.get("page", 1), per_page=10)

        context = {
            "workareas": workareas,
            "patienttable": patienttable,
            "filter": filter,
        }
        return render(request, template, context)


@login_required(login_url="login_billing")
def order_add_patient(request):
    workareas = models.Workarea.objects.all().order_by("sort")
    if request.method == "POST":
        form = forms.PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            return redirect("create_order_from_patient", patient_pk=patient.pk)
        else:
            template = "select/add_patient.html"
            context = {"workareas": workareas, "form": form}
            return render(request, template, context)
    else:
        template = "select/add_patient.html"
        context = {"workareas": workareas, "form": forms.PatientForm}
        return render(request, template, context)


@login_required(login_url="login_billing")
def create_order_from_patient(request, patient_pk):
    patient = models.Patients.objects.get(pk=patient_pk)
    order = patient.create_order()
    return redirect("order_edit", pk=order.pk)


@login_required(login_url="login_billing")
def order_print_receipt(request, order_pk):
    report_content = ""
    res_rep = report.JasperServer()
    b_ok, content = res_rep.get_report_order(order_pk, "order_receipt", "html")
    if b_ok:
        response = HttpResponse(content)
    else:
        response = JsonResponse(content)

    return response


@login_required(login_url="login_billing")
def order_print_receipt_old(request, order_pk):
    order = models.Orders.objects.get(pk=order_pk)
    org_lab_name = models.Parameters.objects.filter(name="ORG_LAB_NAME")
    org_lab_address = models.Parameters.objects.filter(name="ORG_LAB_ADDRESS")
    org_lab_city = models.Parameters.objects.filter(name="ORG_LAB_CITY")
    template = "corelab/order_print_receipt.html"
    context = {
        "order": order,
        "org_lab_name": org_lab_name,
        "org_lab_address": org_lab_address,
        "org_lab_city": org_lab_city,
    }
    return render(request, template, context)


@login_required(login_url="login_billing")
def order_print_bill(request, order_pk):
    report_content = ""
    res_rep = report.JasperServer()
    b_ok, content = res_rep.get_report_order(order_pk, "order_bill", "html")
    if b_ok:
        response = HttpResponse(content)
    else:
        response = JsonResponse(content)

    return response


@login_required(login_url="login_billing")
def order_print_bill_old(request, order_pk):
    order = models.Orders.objects.get(pk=order_pk)
    org_lab_name = models.Parameters.objects.filter(name="ORG_LAB_NAME")
    org_lab_address = models.Parameters.objects.filter(name="ORG_LAB_ADDRESS")
    org_lab_city = models.Parameters.objects.filter(name="ORG_LAB_CITY")
    template = "corelab/order_print_bill.html"
    context = {
        "order": order,
        "org_lab_name": org_lab_name,
        "org_lab_address": org_lab_address,
        "org_lab_city": org_lab_city,
    }
    return render(request, template, context)


@login_required(login_url="login_billing")
def order_print_worklist(request, order_pk):
    order = models.Orders.objects.get(pk=order_pk)
    org_lab_name = models.Parameters.objects.filter(name="ORG_LAB_NAME")
    org_lab_address = models.Parameters.objects.filter(name="ORG_LAB_ADDRESS")
    org_lab_city = models.Parameters.objects.filter(name="ORG_LAB_CITY")
    template = "corelab/order_print_worklist.html"
    context = {
        "order": order,
        "org_lab_name": org_lab_name,
        "org_lab_address": org_lab_address,
        "org_lab_city": org_lab_city,
    }
    return render(request, template, context)


@login_required(login_url="login_billing")
def order_print_barcode(request, order_pk):
    order = models.Orders.objects.get(pk=order_pk)

    MESSAGE_TAGS = {messages.ERROR: "danger"}

    printer_id = request.GET.get("printer")

    p_label = Label()
    p_label.set_order_id(order_pk)
    p_label.set_labelprinter_id(printer_id)

    not_err, msg = p_label.print_label()

    if not_err:
        messages.info(request, msg)
    else:
        messages.error(
            request, "Error when printer label [%s]" % msg, extra_tags="danger"
        )

    return redirect("order_detail", pk=order.pk)


@login_required(login_url="login_billing")
def order_sample_label(request):
    order_sample_id = request.GET["order_sample_id"]
    printer_id = request.GET["printer"]

    o_order_sample = models.OrderSamples.objects.get(pk=order_sample_id)
    order = models.Orders.objects.filter(pk=o_order_sample.order_id)
    o_order = models.Orders.objects.get(pk=o_order_sample.order_id)
    order_sample = models.OrderSamples.objects.filter(order=o_order)
    request_new_data = models.RequestNewReasons.objects.all()
    label_printer = models.LabelPrinters.objects.filter(active=True)

    MESSAGE_TAGS = {messages.ERROR: "danger"}

    printer_id = request.GET.get("printer")

    p_label = Label()
    p_label.set_order_sample_id(order_sample_id)
    p_label.set_labelprinter_id(printer_id)

    not_err, msg = p_label.print_label()

    if not_err:
        messages.info(request, msg)
    else:
        messages.error(
            request, "Error when printer label [%s]" % msg, extra_tags="danger"
        )

    context = {
        "orderno": o_order.number,
        "order": order,
        "samples": order_sample,
        "request_new_data": request_new_data,
        "label_printer": label_printer,
    }

    return render(request, "corelab/sample_receive.html", context=context)

    return redirect("order_detail", pk=order.pk)


@login_required(login_url="login_billing")
def worklist_print(request, pk):
    worklist = models.Worklists.objects.get(pk=pk)
    worklist_order = models.WorklistOrders.objects.filter(worklist=pk)
    org_lab_name = models.Parameters.objects.filter(name="ORG_LAB_NAME")
    org_lab_address = models.Parameters.objects.filter(name="ORG_LAB_ADDRESS")
    org_lab_city = models.Parameters.objects.filter(name="ORG_LAB_CITY")
    template = "corelab/worklist_print.html"
    context = {
        "worklist": worklist,
        "worklist_order": worklist_order,
        "org_lab_name": org_lab_name,
        "org_lab_address": org_lab_address,
        "org_lab_city": org_lab_city,
    }
    return render(request, template, context)

    return redirect("order_detail", pk=order.pk)


@login_required(login_url="login_billing")
def order_send_lis(request, order_pk):
    order = models.Orders.objects.get(pk=order_pk)
    # seding to LIS here
    ts = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    filename = settings.HL7_ORDER_DIR + "order_" + order.number + "_" + ts + ".hl7"
    handle1 = open(filename, "w+")
    content_hl7 = ""
    content_hl7 += (
        "MSH|^~\&|BIL|BIL-DREAM|CIT-INFINITY|LabPK|||ORM^O01|" + ts + "||||||ER|\r"
    )
    content_hl7 += (
        "PID|||"
        + order.patient.patient_id
        + "||"
        + order.patient.name
        + "||"
        + order.patient.gender.ext_code
        + "|"
        + DateFormat(order.patient.dob).format("Ymd")
        + "|||"
        + order.patient.address
        + "^^^||\r"
    )
    # content_hl7 += 'PV1|||||||||||'+order.doctor.ext_code+'^'+order.doctor.name+'^'+order.diagnosis.ext_code+'^'+order.diagnosis.name+'^^||\r'
    content_hl7 += (
        "PV1|||||||||||" + order.doctor.ext_code + "^" + order.doctor.name + "^^^^||\r"
    )
    content_hl7 += (
        "ORC|NW|"
        + order.number
        + "|||"
        + order.origin.ext_code
        + "|"
        + order.origin.name
        + "|"
        + order.priority.ext_code
        + "|"
        + order.insurance.ext_code
        + "^"
        + order.insurance.name
        + "|"
        + ts
        + "||||||01||\r"
    )
    i = 1
    for tes in order.order_items.all():
        content_hl7 += (
            "OBR|"
            + str(i)
            + "|||"
            + tes.test.ext_code
            + "|"
            + tes.test.name
            + "||"
            + ts
            + "||||A\r"
        )
        i += 1
    handle1.write(content_hl7)
    handle1.close()
    messages.info(request, "Created file HL7 [" + filename + "]")
    return redirect("order_detail", pk=order.pk)


#####################
# Lab function
#####################
@login_required(login_url="login_billing")
def show_workarea_group(request, pk):
    wa_group = models.Workarea.objects.get(pk=pk)

    test_group = models.WorkareaTestGroups.objects.filter(workarea=wa_group).values(
        "testgroup"
    )

    # order_wa = models.OrderTests.objects.filter(test__test_group__in=test_group).values('order')

    order_wa = models.OrderResults.objects.filter(
        test__test_group__in=test_group
        # , validation_status__lte=3
    ).values("order")

    data = models.Orders.objects.filter(pk__in=order_wa)

    request.GET = request.GET.copy()
    s = request.GET.get("number")
    if s:
        request.GET["number"] = "".join([i for i in s if i.isnumeric()])

    filter = filters.WokareaFilter(request.GET, queryset=data)

    ordertable = tables.OrderResultTableWa(filter.qs)
    ordertable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(ordertable)

    template = "corelab/workarea_group.html"
    workareas = models.Workarea.objects.all().order_by("sort")
    capture_filter = models.UserWorkareaFilter.objects.filter(user=request.user)
    context = {
        "area_pk": pk,
        "wa_group": wa_group,
        "workareas": workareas,
        "ordertable": ordertable,
        "filter": filter,
        "capture_filter": capture_filter,
    }
    return render(request, template, context)


@login_required(login_url="login_billing")
def capture_workarea(request, area_pk):
    workarea = models.Workarea.objects.get(pk=area_pk)
    if request.method == "POST":
        # print  request.POST
        userwa = models.UserWorkareaFilter()
        userwa.user = request.user
        userwa.workarea = workarea
        userwa.name = request.POST.get("name", "")
        userwa.filter_set = request.POST.get("path", "")
        b_def = False
        if request.POST.get("default", "") == "on":
            # update to false default other filter
            usewa_def = models.UserWorkareaFilter.objects.filter(
                user=request.user
            ).update(default=False)
            b_def = True

        userwa.default = b_def
        userwa.save()
        return redirect(request.POST.get("path", ""))

    return redirect("workarea_group", area_pk)


@login_required(login_url="login_billing")
def show_workarea(request):
    workareas = models.Workarea.objects.all().order_by("sort")
    order_wa = models.OrderResults.objects.values(
        "order"
    )
    data = models.Orders.objects.filter(pk__in=order_wa)
    # data = models.Orders.objects.all()

    request.GET = request.GET.copy()
    s = request.GET.get("number")
    if s:
        request.GET["number"] = "".join([i for i in s if i.isnumeric()])

    filter = filters.WokareaFilter(request.GET, queryset=data)
    ordertable = tables.OrderResultTable(filter.qs)
    ordertable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(ordertable)

    tempate = "middleware/workarea.html"
    context = {"workareas": workareas, "ordertable": ordertable, "filter": filter}
    return render(request, tempate, context)


@login_required(login_url="login_billing")
def order_results_history(request, pk):
    workareas = models.Workarea.objects.all().order_by("sort")
    order = models.Orders.objects.get(pk=pk)
    data = models.HistoryOrders.objects.filter(order_id=pk)

    if request.GET.get("test"):
        # print request.GET.get('test')
        data = data.filter(test=request.GET.get("test"))

    if request.GET.get("action_user"):
        # print request.GET.get('action_user')
        data = data.filter(action_user__contains=request.GET.get("action_user"))

    if request.GET.get("action_code"):
        # print request.GET.get('action_code')
        data = data.filter(action_code__contains=request.GET.get("action_code"))

    if request.GET.get("action_text"):
        # print request.GET.get('action_text')
        data = data.filter(action_text__contains=request.GET.get("action_text"))

    filter = filters.OrderHistoryFilter(request.GET, queryset=data)

    orderhist = tables.OrderHistoryTable(data)
    orderhist.paginate(page=request.GET.get("page", 1), per_page=20)
    tempate = "middleware/order_history.html"
    context = {
        "workareas": workareas,
        "order": order,
        "orderhist": orderhist,
        "filter": filter,
    }
    return render(request, tempate, context)


@login_required(login_url="login_billing")
def workarea_order_results_history(request, order_pk, area_pk):
    workareas = models.Workarea.objects.all().order_by("sort")
    order = models.Orders.objects.get(pk=order_pk)
    data = models.HistoryOrders.objects.filter(order_id=order_pk)
    wa_group = models.Workarea.objects.get(pk=area_pk)

    if request.GET.get("test"):
        # print request.GET.get('test')
        data = data.filter(test=request.GET.get("test"))

    if request.GET.get("action_user"):
        # print request.GET.get('action_user')
        data = data.filter(action_user__contains=request.GET.get("action_user"))

    if request.GET.get("action_code"):
        # print request.GET.get('action_code')
        data = data.filter(action_code__contains=request.GET.get("action_code"))

    if request.GET.get("action_text"):
        # print request.GET.get('action_text')
        data = data.filter(action_text__contains=request.GET.get("action_text"))

    filter = filters.OrderHistoryFilter(request.GET, queryset=data)

    orderhist = tables.OrderHistoryTable(data)
    orderhist.paginate(page=request.GET.get("page", 1), per_page=20)
    tempate = "corelab/order_history_wa.html"
    context = {
        "workareas": workareas,
        "order": order,
        "orderhist": orderhist,
        "filter": filter,
        "wa_group": wa_group,
        "area_pk": area_pk,
    }
    return render(request, tempate, context)


@login_required(login_url="login_billing")
def order_results_validate(request, pk):
    if request.user.is_authenticated():
        order_res = models.OrderResults.objects.filter(
            order_id=pk, validation_status=1
        ).update(
            validation_status=2,
            validation_user=str(request.user),
            validation_date=timezone.now(),
        )
    return redirect("order_results", pk=pk)


@login_required(login_url="login_billing")
def order_results_techval(request, pk):
    if request.user.is_authenticated():
        # create history
        tech_val = models.OrderResults.objects.filter(
            order_id=pk, validation_status=1
        ).values("test_id")
        for tes in tech_val:
            test_id = tes["test_id"]
            test = models.Tests.objects.get(pk=test_id)
            act_txt = "Test %s technical validated" % (test)
            his_order = models.HistoryOrders(
                order_id=pk,
                test=test,
                action_code="TECHVAL",
                action_user=str(request.user),
                action_date=timezone.now(),
                action_text=act_txt,
            )
            his_order.save()

        # update
        order_res = models.OrderResults.objects.filter(
            order_id=pk, validation_status=1
        ).update(
            validation_status=2,
            techval_user=str(request.user),
            techval_date=timezone.now(),
        )
    return redirect("order_results", pk=pk)


@login_required(login_url="login_billing")
def order_results_medval(request, pk):
    if request.user.is_authenticated():
        # create history
        med_val = models.OrderResults.objects.filter(
            order_id=pk, validation_status=2
        ).values("test_id")
        for tes in med_val:
            test_id = tes["test_id"]
            test = models.Tests.objects.get(pk=test_id)
            act_txt = "Test %s medical validated" % (test)
            his_order = models.HistoryOrders(
                order_id=pk,
                test=test,
                action_code="MEDVAL",
                action_user=str(request.user),
                action_date=timezone.now(),
                action_text=act_txt,
            )
            his_order.save()
        order_res = models.OrderResults.objects.filter(
            order_id=pk, validation_status=2
        ).update(
            validation_status=3,
            medval_user=str(request.user),
            medval_date=timezone.now(),
        )
    return redirect("order_results", pk=pk)


@login_required(login_url="login_billing")
def order_results_repeat(request, pk):
    return redirect("order_results", pk=pk)


@login_required(login_url="login_billing")
def order_results_print_old(request, pk):
    order = models.Orders.objects.get(pk=pk)

    input_file_header = settings.RESULT_REPORT_FILE_HEADER
    input_file_footer = settings.RESULT_REPORT_FILE_FOOTER
    input_file_main = settings.RESULT_REPORT_FILE_MAIN
    input_file = settings.RESULT_REPORT_FILE

    ts = datetime.today().strftime("%Y%m%d%H%M%S")
    parameters = {"ORDER_ID": pk}
    output = settings.MEDIA_ROOT + "\\report\\" + str(order.number) + "_" + ts
    con = settings.JASPER_CONN

    jasper = JasperPy()

    jasper.compile(input_file_header)
    jasper.compile(input_file_footer)
    jasper.compile(input_file_main)

    jasper.process(
        input_file,
        output_file=output,
        format_list=["pdf"],
        parameters=parameters,
        db_connection=con,
        locale="id_ID",
        resource=settings.RESULT_REPORT_DIR,
    )

    base_url = request.build_absolute_uri("/")[:-1].strip("/")
    url_pdf = base_url + "/media/report/" + str(order.number) + "_" + ts + ".pdf"

    # save report URL
    oe, _created = models.OrderExtended.objects.get_or_create(order_id=pk)

    oe.result_pdf_url = url_pdf
    oe.save()

    # set validation printed
    if request.user.is_authenticated():
        order_res = models.OrderResults.objects.filter(
            order_id=pk, validation_status=3
        ).update(
            validation_status=4, print_user=str(request.user), print_date=timezone.now()
        )

    template = "middleware/result_pdf_preview.html"
    context = {"order": order, "url_pdf": url_pdf}
    return render(request, template, context)


@login_required(login_url="login_billing")
def order_results_print(request, pk):
    order = models.Orders.objects.get(pk=pk)

    group_id = request.GET.get("group_id")

    input_file_header = settings.RESULT_REPORT_FILE_HEADER
    input_file_footer = settings.RESULT_REPORT_FILE_FOOTER
    input_file_main = settings.RESULT_REPORT_FILE_MAIN
    input_file = settings.RESULT_REPORT_FILE

    ts = datetime.today().strftime("%Y%m%d%H%M%S")
    parameters = {"ORDER_ID": pk}
    output = settings.MEDIA_ROOT + "\\report\\" + str(order.number) + "_" + ts + ".pdf"
    con = settings.JASPER_CONN

    res_rep = report.JasperServer()

    b_ok, content = res_rep.get_report(pk, group_id)

    # print b_ok

    # print content

    if b_ok:
        fd = open(output, "wb")
        fd.write(content)
        fd.close()

        base_url = request.build_absolute_uri("/")[:-1].strip("/")
        url_pdf = base_url + "/media/report/" + str(order.number) + "_" + ts + ".pdf"

        # save report URL
        oe, _created = models.OrderExtended.objects.get_or_create(order_id=pk)

        oe.result_pdf_url = url_pdf
        oe.save()

        # set validation printed
        if request.user.is_authenticated():
            order_res = models.OrderResults.objects.filter(
                order_id=pk, validation_status=3
            ).update(
                validation_status=4,
                print_user=str(request.user),
                print_date=timezone.now(),
            )

        template = "middleware/result_pdf_preview.html"
        context = {"order": order, "url_pdf": url_pdf}
        return render(request, template, context)
    else:
        return JsonResponse(content)


@login_required(login_url="login_billing")
def order_results_print_wa(request, area_pk, order_pk):
    order = models.Orders.objects.get(pk=order_pk)

    group_id = request.GET.get("group_id")

    # print group_id

    input_file_header = settings.RESULT_REPORT_FILE_HEADER
    input_file_footer = settings.RESULT_REPORT_FILE_FOOTER
    input_file_main = settings.RESULT_REPORT_FILE_MAIN
    input_file = settings.RESULT_REPORT_FILE

    ts = datetime.today().strftime("%Y%m%d%H%M%S")
    parameters = {"ORDER_ID": order_pk}
    output = settings.MEDIA_ROOT + "\\report\\" + str(order.number) + "_" + ts + ".pdf"
    con = settings.JASPER_CONN

    res_rep = report.JasperServer()

    b_ok, content = res_rep.get_report(order_pk, group_id)

    # print b_ok

    # print content

    if b_ok:
        fd = open(output, "wb")
        fd.write(content)
        fd.close()

        base_url = request.build_absolute_uri("/")[:-1].strip("/")
        url_pdf = base_url + "/media/report/" + str(order.number) + "_" + ts + ".pdf"

        # save report URL
        oe, _created = models.OrderExtended.objects.get_or_create(order_id=order_pk)

        oe.result_pdf_url = url_pdf
        oe.save()

        # set validation printed
        if request.user.is_authenticated():
            order_res = models.OrderResults.objects.filter(
                order_id=order_pk, validation_status=3
            ).update(
                validation_status=4,
                print_user=str(request.user),
                print_date=timezone.now(),
            )

        template = "middleware/result_pdf_preview.html"
        context = {"order": order, "url_pdf": url_pdf}
        return render(request, template, context)
    else:
        return JsonResponse(content)


@login_required(login_url="login_billing")
def order_result_report(request, pk):
    template = "middleware/result_pdf_preview.html"
    context = {"order": order, "url_pdf": url_pdf}
    return render(request, template, context)


@login_required(login_url="login_billing")
def order_result_print_draft(request, pk):
    testgroup_id = request.GET.get("testgroup_id")
    order = models.Orders.objects.get(pk=pk)
    testgroup = models.TestGroups.objects.get(pk=testgroup_id)
    org_lab_name = models.Parameters.objects.filter(name="ORG_LAB_NAME")
    org_lab_address = models.Parameters.objects.filter(name="ORG_LAB_ADDRESS")
    org_lab_city = models.Parameters.objects.filter(name="ORG_LAB_CITY")
    template = "report/draft_report.html"
    context = {
        "order": order,
        "testgroup": testgroup,
        "org_lab_name": org_lab_name,
        "org_lab_address": org_lab_address,
        "org_lab_city": org_lab_city,
    }
    return render(request, template, context)


@login_required(login_url="login_billing")
def order_results(request, pk):
    order = models.Orders.objects.get(pk=pk)
    if request.method == "POST":
        repeat_conclusion = False
        save = False
        repeat = False
        techval = False
        medval = False
        delete = False
        for par in request.POST:
            if par == "save":
                save = True
            if par == "repeat":
                repeat = True
            if par == "repeat_conclusion":
                repeat_conclusion = True
            if par == "techval":
                techval = True
            if par == "medval":
                medval = True
            if par == "delete":
                delete = True

        for p_tes in request.POST:
            # print request.POST
            if p_tes == "conclusion" and not repeat_conclusion:
                # conclusion
                s_con = request.POST.get(p_tes, "")
                if s_con != "":
                    o_order = models.Orders.objects.get(pk=pk)
                    if o_order.conclusion != s_con:
                        o_order.conclusion = s_con
                        o_order.save()
                        # update history
                        act_txt = "Edit conclusion to [%s]" % s_con
                        his_order = models.HistoryOrders(
                            order=o_order,
                            action_code="CONCL",
                            action_user=str(request.user),
                            action_date=timezone.now(),
                            action_text=act_txt,
                        )
                        his_order.save()

            if p_tes.startswith("test_") and save:
                o_order = models.Orders.objects.get(pk=pk)
                o_test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                o_result = request.POST.get(p_tes, "")

                # print 'tes save result'
                # print o_order
                # print o_test
                # print o_result
                # check current result
                if request.POST.get(p_tes, "") != "":
                    # get current result
                    cr_res_a = ""
                    try:
                        cr_res = models.OrderResults.objects.get(
                            order=o_order, test=o_test
                        )
                        cr_res_a = cr_res.result.alfa_result
                    except:
                        pass

                    if not cr_res_a == request.POST.get(p_tes, ""):
                        if request.user.is_authenticated():
                            alfa_res = request.POST.get(p_tes, "")
                            o_result = models.Results(
                                order=o_order, test=o_test, alfa_result=alfa_res
                            )
                            o_result.save()

                            flag = None

                            ord_res = models.OrderResults.objects.get(
                                order=o_order, test=o_test
                            )

                            try:
                                if is_float(alfa_res) and ord_res.ref_range:
                                    if str(ord_res.ref_range).find(" - ") > 0:
                                        # range
                                        range = str(ord_res.ref_range).split(" - ")
                                        if (
                                            float(range[0])
                                            <= float(alfa_res)
                                            <= float(range[1])
                                        ):
                                            flag = "N"
                                        elif float(alfa_res) >= float(range[1]):
                                            flag = "H"
                                        else:
                                            flag = "L"
                                    elif "<" in str(ord_res.ref_range) or ">" in str(
                                        ord_res.ref_range
                                    ):
                                        range = str(ord_res.ref_range).split(" ")
                                        if str(range[0]) == ">":
                                            if float(alfa_res) > float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "L"
                                        elif str(range[0]) == "<":
                                            if float(alfa_res) < float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                                        elif str(range[0]) == ">=":
                                            if float(alfa_res) >= float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                                        elif str(range[0]) == "<=":
                                            if float(alfa_res) <= float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                            except ValueError:
                                print("Fail setup ref.ranges [%s] " % ord_res.ref_range)

                            else:
                                flag = "A"

                            ord_res.result = o_result
                            # ord_res.patologi_mark = flag
                            ord_res.validation_status = 1
                            ord_res.techval_user = None
                            ord_res.techval_date = None
                            ord_res.medval_user = None
                            ord_res.medval_date = None
                            ord_res.save()

                            # create history
                            act_txt = "Result %s set for analyt %s " % (
                                request.POST.get(p_tes, ""),
                                o_test,
                            )
                            his_order = models.HistoryOrders(
                                order=o_order,
                                test=o_test,
                                action_code="RESENTRY",
                                action_user=str(request.user),
                                action_date=timezone.now(),
                                action_text=act_txt,
                            )
                            his_order.save()

            if p_tes.startswith("check_") and techval:
                if is_float(p_tes.split("_")[1]):
                    o_order = models.Orders.objects.get(pk=pk)
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    # update
                    order_res = models.OrderResults.objects.filter(
                        order=o_order, test=test, validation_status=1
                    ).update(
                        validation_status=2,
                        techval_user=str(request.user),
                        techval_date=timezone.now(),
                    )
                    # history
                    act_txt = "Test %s technical validated" % (test)
                    his_order = models.HistoryOrders(
                        order_id=pk,
                        test=test,
                        action_code="TECHVAL",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and medval:
                if is_float(p_tes.split("_")[1]):
                    o_order = models.Orders.objects.get(pk=pk)
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    # update
                    order_res = models.OrderResults.objects.filter(
                        order=o_order, test=test, validation_status=2
                    ).update(
                        validation_status=3,
                        medval_user=str(request.user),
                        medval_date=timezone.now(),
                    )
                    # history
                    act_txt = "Test %s medical validated" % (test)
                    his_order = models.HistoryOrders(
                        order_id=pk,
                        test=test,
                        action_code="MEDVAL",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and delete:
                o_order = models.Orders.objects.get(pk=pk)
                if is_float(p_tes.split("_")[1]):
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    ord_res = models.OrderResults.objects.get(order=o_order, test=test)
                    ord_res.delete()
                    # delete
                    ord_test = models.OrderTests.objects.get(order=o_order, test=test)
                    ord_test.delete()
                    # order_res = models.OrderResults.objects.filter(order=o_order,test=test,validation_status=1).update(validation_status=2,techval_user=str(request.user),techval_date=timezone.now())
                    # history
                    act_txt = "Test %s deleted" % (test)
                    his_order = models.HistoryOrders(
                        order_id=pk,
                        test=test,
                        action_code="DELETE",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and repeat:
                if p_tes == "check_conclusion":
                    cl = models.Orders.objects.get(pk=pk)
                    cl.conclusion = ""
                    cl.save()
                    # create history
                    act_txt = "Conclusion is repeated"
                    his_order = models.HistoryOrders(
                        order=order,
                        action_code="CONCREPEAT",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()
                    repeat_conclusion = True
                if p_tes != "check_conclusion":
                    if is_float(p_tes.split("_")[1]):
                        o_order = models.Orders.objects.get(pk=pk)
                        tes = models.Tests.objects.get(pk=p_tes.split("_")[1])
                        result = models.Results(order=order, test=tes)
                        result.save()
                        order_result = models.OrderResults.objects.get(
                            order=order, test=tes
                        )
                        order_result.validation_status = 0
                        order_result.result = result
                        order_result.techval_user = None
                        order_result.techval_date = None
                        order_result.medval_user = None
                        order_result.medval_date = None
                        order_result.patologi_mark = None
                        order_result.save()
                        order_res = models.OrderResults.objects.filter(
                            order_id=pk, validation_status=1
                        ).update(
                            validation_status=3,
                            medval_user=str(request.user),
                            medval_date=timezone.now(),
                        )

                        # create history
                        act_txt = "Result %s repeated" % (tes)
                        his_order = models.HistoryOrders(
                            order=order,
                            test=tes,
                            action_code="REPEAT",
                            action_user=str(request.user),
                            action_date=timezone.now(),
                            action_text=act_txt,
                        )
                        his_order.save()

    # Reference Range update from

    orders = models.Orders.objects.get(pk=pk)
    ordertests = (
        models.OrderResults.objects.filter(order=orders)
        .values(
            "test_id",
            "test__test_group__name",
            "test__name",
            "test__result_type",
            "result__alfa_result",
            "is_header",
            "unit",
            "ref_range",
            "patologi_mark",
            "validation_status",
            "result__instrument__name",
            "techval_user",
            "medval_user",
        )
        .order_by("test__test_group__sort", "test__sort")
    )
    # .distinct()

    # print ordertests.query
    # save report URL
    if ordertests.count() == 0:
        messages.warning(
            request, _("Test is empty, Do you forget to print the sample barcode?")
        )
    oe, _created = models.OrderExtended.objects.get_or_create(order_id=pk)

    # testgroup = models.TestGroups.objects.all()
    # testgroup = models.OrderResults.
    # testgroup = models.OrderResults.objects.filter(order=o).values('test__test_group','test__test_group__name')
    testgroup = (
        models.OrderResults.objects.filter(order_id=pk)
        .values("test__test_group", "test__test_group__name")
        .distinct()
        .order_by("-test__test_group")
    )
    tempate = "middleware/order_results.html"
    workareas = models.Workarea.objects.all().order_by("sort")
    context = {
        "workareas": workareas,
        "order": order,
        "orders": orders,
        "ordertests": ordertests,
        "testgroup": testgroup,
    }
    return render(request, tempate, context)


@login_required(login_url="login_billing")
def complete_results(request, pk):
    order = models.Orders.objects.get(pk=pk)
    if request.method == "POST":
        repeat_conclusion = False
        save = False
        repeat = False
        techval = False
        medval = False
        delete = False
        for par in request.POST:
            if par == "save":
                save = True
            if par == "repeat":
                repeat = True
            if par == "repeat_conclusion":
                repeat_conclusion = True
            if par == "techval":
                techval = True
            if par == "medval":
                medval = True
            if par == "delete":
                delete = True

        for p_tes in request.POST:
            # print request.POST
            if p_tes == "conclusion" and not repeat_conclusion:
                # conclusion
                s_con = request.POST.get(p_tes, "")
                if s_con != "":
                    o_order = models.Orders.objects.get(pk=pk)
                    if o_order.conclusion != s_con:
                        o_order.conclusion = s_con
                        o_order.save()
                        # update history
                        act_txt = "Edit conclusion to [%s]" % s_con
                        his_order = models.HistoryOrders(
                            order=o_order,
                            action_code="CONCL",
                            action_user=str(request.user),
                            action_date=timezone.now(),
                            action_text=act_txt,
                        )
                        his_order.save()

            if p_tes.startswith("test_") and save:
                o_order = models.Orders.objects.get(pk=pk)
                o_test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                o_result = request.POST.get(p_tes, "")

                # print 'tes save result'
                # print o_order
                # print o_test
                # print o_result
                # check current result
                if request.POST.get(p_tes, "") != "":
                    # get current result
                    cr_res_a = ""
                    try:
                        cr_res = models.OrderResults.objects.get(
                            order=o_order, test=o_test
                        )
                        cr_res_a = cr_res.result.alfa_result
                    except:
                        pass

                    if not cr_res_a == request.POST.get(p_tes, ""):
                        if request.user.is_authenticated():
                            alfa_res = request.POST.get(p_tes, "")
                            o_result = models.Results(
                                order=o_order, test=o_test, alfa_result=alfa_res
                            )
                            o_result.save()

                            flag = None

                            ord_res = models.OrderResults.objects.get(
                                order=o_order, test=o_test
                            )

                            try:
                                if is_float(alfa_res) and ord_res.ref_range:
                                    if str(ord_res.ref_range).find(" - ") > 0:
                                        # range
                                        range = str(ord_res.ref_range).split(" - ")
                                        if (
                                            float(range[0])
                                            <= float(alfa_res)
                                            <= float(range[1])
                                        ):
                                            flag = "N"
                                        elif float(alfa_res) >= float(range[1]):
                                            flag = "H"
                                        else:
                                            flag = "L"
                                    elif "<" in str(ord_res.ref_range) or ">" in str(
                                        ord_res.ref_range
                                    ):
                                        range = str(ord_res.ref_range).split(" ")
                                        if str(range[0]) == ">":
                                            if float(alfa_res) > float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "L"
                                        elif str(range[0]) == "<":
                                            if float(alfa_res) < float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                                        elif str(range[0]) == ">=":
                                            if float(alfa_res) >= float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                                        elif str(range[0]) == "<=":
                                            if float(alfa_res) <= float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                            except ValueError:
                                print("Fail setup ref.ranges [%s] " % ord_res.ref_range)

                            else:
                                flag = "A"

                            ord_res.result = o_result
                            # ord_res.patologi_mark = flag
                            ord_res.validation_status = 1
                            ord_res.techval_user = None
                            ord_res.techval_date = None
                            ord_res.medval_user = None
                            ord_res.medval_date = None
                            ord_res.save()

                            # create history
                            act_txt = "Result %s set for analyt %s " % (
                                request.POST.get(p_tes, ""),
                                o_test,
                            )
                            his_order = models.HistoryOrders(
                                order=o_order,
                                test=o_test,
                                action_code="RESENTRY",
                                action_user=str(request.user),
                                action_date=timezone.now(),
                                action_text=act_txt,
                            )
                            his_order.save()

            if p_tes.startswith("check_") and techval:
                if is_float(p_tes.split("_")[1]):
                    o_order = models.Orders.objects.get(pk=pk)
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    # update
                    order_res = models.OrderResults.objects.filter(
                        order=o_order, test=test, validation_status=1
                    ).update(
                        validation_status=2,
                        techval_user=str(request.user),
                        techval_date=timezone.now(),
                    )
                    # history
                    act_txt = "Test %s technical validated" % (test)
                    his_order = models.HistoryOrders(
                        order_id=pk,
                        test=test,
                        action_code="TECHVAL",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and medval:
                if is_float(p_tes.split("_")[1]):
                    o_order = models.Orders.objects.get(pk=pk)
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    # update
                    order_res = models.OrderResults.objects.filter(
                        order=o_order, test=test, validation_status=2
                    ).update(
                        validation_status=3,
                        medval_user=str(request.user),
                        medval_date=timezone.now(),
                    )
                    # history
                    act_txt = "Test %s medical validated" % (test)
                    his_order = models.HistoryOrders(
                        order_id=pk,
                        test=test,
                        action_code="MEDVAL",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and delete:
                o_order = models.Orders.objects.get(pk=pk)
                if is_float(p_tes.split("_")[1]):
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    ord_res = models.OrderResults.objects.get(order=o_order, test=test)
                    ord_res.delete()
                    # delete
                    ord_test = models.OrderTests.objects.get(order=o_order, test=test)
                    ord_test.delete()
                    # order_res = models.OrderResults.objects.filter(order=o_order,test=test,validation_status=1).update(validation_status=2,techval_user=str(request.user),techval_date=timezone.now())
                    # history
                    act_txt = "Test %s deleted" % (test)
                    his_order = models.HistoryOrders(
                        order_id=pk,
                        test=test,
                        action_code="DELETE",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and repeat:
                if p_tes == "check_conclusion":
                    cl = models.Orders.objects.get(pk=pk)
                    cl.conclusion = ""
                    cl.save()
                    # create history
                    act_txt = "Conclusion is repeated"
                    his_order = models.HistoryOrders(
                        order=order,
                        action_code="CONCREPEAT",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()
                    repeat_conclusion = True
                if p_tes != "check_conclusion":
                    if is_float(p_tes.split("_")[1]):
                        o_order = models.Orders.objects.get(pk=pk)
                        tes = models.Tests.objects.get(pk=p_tes.split("_")[1])
                        result = models.Results(order=order, test=tes)
                        result.save()
                        order_result = models.OrderResults.objects.get(
                            order=order, test=tes
                        )
                        order_result.validation_status = 0
                        order_result.result = result
                        order_result.techval_user = None
                        order_result.techval_date = None
                        order_result.medval_user = None
                        order_result.medval_date = None
                        # order_result.patologi_mark = None
                        order_result.save()
                        order_res = models.OrderResults.objects.filter(
                            order_id=pk, validation_status=1
                        ).update(
                            validation_status=3,
                            medval_user=str(request.user),
                            medval_date=timezone.now(),
                        )

                        # create history
                        act_txt = "Result %s repeated" % (tes)
                        his_order = models.HistoryOrders(
                            order=order,
                            test=tes,
                            action_code="REPEAT",
                            action_user=str(request.user),
                            action_date=timezone.now(),
                            action_text=act_txt,
                        )
                        his_order.save()

    # Reference Range update from

    orders = models.Orders.objects.get(pk=pk)
    ordertests = (
        models.OrderResults.objects.filter(order=orders)
        .values(
            "test_id",
            "test__test_group__name",
            "test__name",
            "test__result_type",
            "result__alfa_result",
            "is_header",
            "unit",
            "ref_range",
            "patologi_mark",
            "validation_status",
            "result__instrument__name",
            "techval_user",
            "medval_user",
        )
        .order_by("test__test_group__sort", "test__sort")
    )
    # .distinct()

    # print ordertests.query
    # save report URL
    if ordertests.count() == 0:
        messages.warning(
            request, _("Test is empty, Do you forget to print the sample barcode?")
        )
    oe, _created = models.OrderExtended.objects.get_or_create(order_id=pk)

    # testgroup = models.TestGroups.objects.all()
    # testgroup = models.OrderResults.
    # testgroup = models.OrderResults.objects.filter(order=o).values('test__test_group','test__test_group__name')
    testgroup = (
        models.OrderResults.objects.filter(order_id=pk)
        .values("test__test_group", "test__test_group__name")
        .distinct()
        .order_by("-test__test_group")
    )
    tempate = "corelab/complete_results.html"
    workareas = models.Workarea.objects.all().order_by("sort")
    context = {
        "workareas": workareas,
        "order": order,
        "orders": orders,
        "ordertests": ordertests,
        "testgroup": testgroup,
    }
    return render(request, tempate, context)


def order_results_wa(request, area_pk, order_pk):
    order = models.Orders.objects.get(pk=order_pk)
    workareas = models.Workarea.objects.all().order_by("sort")
    wa_group = models.Workarea.objects.get(pk=area_pk)
    test_group = models.WorkareaTestGroups.objects.filter(workarea=wa_group).values(
        "testgroup"
    )
    if request.method == "POST":
        repeat_conclusion = False
        save = False
        repeat = False
        techval = False
        medval = False
        delete = False
        for par in request.POST:
            if par == "save":
                save = True
            if par == "repeat":
                repeat = True
            if par == "repeat_conclusion":
                repeat_conclusion = True
            if par == "techval":
                techval = True
            if par == "medval":
                medval = True
            if par == "delete":
                delete = True

        for p_tes in request.POST:
            # print request.POST
            if p_tes == "conclusion" and not repeat_conclusion:
                # conclusion
                s_con = request.POST.get(p_tes, "")
                if s_con != "":
                    o_order = models.Orders.objects.get(pk=order_pk)
                    if o_order.conclusion != s_con:
                        o_order.conclusion = s_con
                        o_order.save()
                        # update history
                        act_txt = "Edit conclusion to [%s]" % s_con
                        his_order = models.HistoryOrders(
                            order=o_order,
                            action_code="CONCL",
                            action_user=str(request.user),
                            action_date=timezone.now(),
                            action_text=act_txt,
                        )
                        his_order.save()

            if p_tes.startswith("test_") and save:
                o_order = models.Orders.objects.get(pk=order_pk)
                o_test = models.Tests.objects.get(pk=p_tes.split("_")[1])

                if request.POST.get(p_tes, "") != "":
                    # get current result
                    cr_res_a = ""
                    try:
                        cr_res = models.OrderResults.objects.get(
                            order=o_order, test=o_test
                        )
                        cr_res_a = cr_res.result.alfa_result
                    except:
                        pass

                    if not cr_res_a == request.POST.get(p_tes, ""):
                        if request.user.is_authenticated():
                            alfa_res = request.POST.get(p_tes, "")
                            o_result = models.Results(
                                order=o_order, test=o_test, alfa_result=alfa_res
                            )
                            o_result.save()

                            flag = None

                            ord_res = models.OrderResults.objects.get(
                                order=o_order, test=o_test
                            )

                            try:
                                if is_float(alfa_res) and ord_res.ref_range:
                                    if str(ord_res.ref_range).find(" - ") > 0:
                                        # range
                                        range = str(ord_res.ref_range).split(" - ")
                                        if (
                                            float(range[0])
                                            <= float(alfa_res)
                                            <= float(range[1])
                                        ):
                                            flag = "N"
                                        elif float(alfa_res) >= float(range[1]):
                                            flag = "H"
                                        else:
                                            flag = "L"
                                    elif "<" in str(ord_res.ref_range) or ">" in str(
                                        ord_res.ref_range
                                    ):
                                        range = str(ord_res.ref_range).split(" ")
                                        if str(range[0]) == ">":
                                            if float(alfa_res) > float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "L"
                                        elif str(range[0]) == "<":
                                            if float(alfa_res) < float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                                        elif str(range[0]) == ">=":
                                            if float(alfa_res) >= float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                                        elif str(range[0]) == "<=":
                                            if float(alfa_res) <= float(range[1]):
                                                flag = "N"
                                            else:
                                                flag = "H"
                            except ValueError:
                                print("Fail setup ref.ranges [%s] " % ord_res.ref_range)

                            else:
                                flag = "A"

                            ord_res.result = o_result
                            # ord_res.patologi_mark = flag
                            ord_res.validation_status = 1
                            ord_res.techval_user = None
                            ord_res.techval_date = None
                            ord_res.medval_user = None
                            ord_res.medval_date = None
                            ord_res.save()

                            # create history
                            act_txt = "Result %s set for analyt %s " % (
                                request.POST.get(p_tes, ""),
                                o_test,
                            )
                            his_order = models.HistoryOrders(
                                order=o_order,
                                test=o_test,
                                action_code="RESENTRY",
                                action_user=str(request.user),
                                action_date=timezone.now(),
                                action_text=act_txt,
                            )
                            his_order.save()

            if p_tes.startswith("check_") and techval:
                if is_float(p_tes.split("_")[1]):
                    o_order = models.Orders.objects.get(pk=order_pk)
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    # update
                    order_res = models.OrderResults.objects.filter(
                        order=o_order, test=test, validation_status=1
                    ).update(
                        validation_status=2,
                        techval_user=str(request.user),
                        techval_date=timezone.now(),
                    )
                    # history
                    act_txt = "Test %s technical validated" % (test)
                    his_order = models.HistoryOrders(
                        order_id=order_pk,
                        test=test,
                        action_code="TECHVAL",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and medval:
                if is_float(p_tes.split("_")[1]):
                    o_order = models.Orders.objects.get(pk=order_pk)
                    test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                    # update
                    order_res = models.OrderResults.objects.filter(
                        order=o_order, test=test, validation_status=2
                    ).update(
                        validation_status=3,
                        medval_user=str(request.user),
                        medval_date=timezone.now(),
                    )
                    # history
                    act_txt = "Test %s medical validated" % (test)
                    his_order = models.HistoryOrders(
                        order_id=order_pk,
                        test=test,
                        action_code="MEDVAL",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and delete:
                o_order = models.Orders.objects.get(pk=order_pk)
                if is_float(p_tes.split("_")[1]):
                    try:
                        test = models.Tests.objects.get(pk=p_tes.split("_")[1])
                        ord_res = models.OrderResults.objects.get(
                            order=o_order, test=test
                        )
                        ord_res.delete()
                        # delete
                        ord_test = models.OrderTests.objects.get(
                            order=o_order, test=test
                        )
                        ord_test.delete()
                    except:
                        pass
                    # order_res = models.OrderResults.objects.filter(order=o_order,test=test,validation_status=1).update(validation_status=2,techval_user=str(request.user),techval_date=timezone.now())
                    # history
                    act_txt = "Test %s deleted" % (test)
                    his_order = models.HistoryOrders(
                        order_id=order_pk,
                        test=test,
                        action_code="DELETE",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()

            if p_tes.startswith("check_") and repeat:
                if p_tes == "check_conclusion":
                    cl = models.Orders.objects.get(pk=order_pk)
                    cl.conclusion = ""
                    cl.save()
                    # create history
                    act_txt = "Conclusion is repeated"
                    his_order = models.HistoryOrders(
                        order=order,
                        action_code="CONCREPEAT",
                        action_user=str(request.user),
                        action_date=timezone.now(),
                        action_text=act_txt,
                    )
                    his_order.save()
                    repeat_conclusion = True
                if p_tes != "check_conclusion":
                    if is_float(p_tes.split("_")[1]):
                        o_order = models.Orders.objects.get(pk=order_pk)
                        tes = models.Tests.objects.get(pk=p_tes.split("_")[1])
                        result = models.Results(order=order, test=tes)
                        result.save()
                        order_result = models.OrderResults.objects.get(
                            order=order, test=tes
                        )
                        order_result.validation_status = 0
                        order_result.result = result
                        order_result.techval_user = None
                        order_result.techval_date = None
                        order_result.medval_user = None
                        order_result.medval_date = None
                        order_result.patologi_mark = None
                        order_result.save()
                        order_res = models.OrderResults.objects.filter(
                            order_id=order_pk, validation_status=1
                        ).update(
                            validation_status=3,
                            medval_user=str(request.user),
                            medval_date=timezone.now(),
                        )

                        # create history
                        act_txt = "Result %s repeated" % (tes)
                        his_order = models.HistoryOrders(
                            order=order,
                            test=tes,
                            action_code="REPEAT",
                            action_user=str(request.user),
                            action_date=timezone.now(),
                            action_text=act_txt,
                        )
                        his_order.save()

    # Reference Range update from

    orders = models.Orders.objects.get(pk=order_pk)
    ordertests = (
        models.OrderResults.objects.filter(
            order=orders, test__test_group__in=test_group
        )
        .values(
            "test_id",
            "test__test_group__name",
            "test__name",
            "test__result_type",
            "result__alfa_result",
            "is_header",
            "unit",
            "ref_range",
            "patologi_mark",
            "validation_status",
            "result__instrument__name",
            "techval_user",
            "medval_user",
        )
        .order_by("test__test_group__sort", "test__sort")
    )
    # .distinct()

    # print ordertests.query
    # save report URL
    if ordertests.count() == 0:
        messages.warning(
            request, _("Test is empty, Do you forget to print the sample barcode?")
        )
    oe, _created = models.OrderExtended.objects.get_or_create(order_id=order_pk)

    # testgroup = models.TestGroups.objects.all()
    # testgroup = models.OrderResults.
    # testgroup = models.OrderResults.objects.filter(order=o).values('test__test_group','test__test_group__name')
    testgroup = (
        models.OrderResults.objects.filter(order_id=order_pk)
        .values("test__test_group", "test__test_group__name")
        .distinct()
        .order_by("-test__test_group")
    )
    # print testgroup
    tempate = "corelab/order_results_wa.html"

    context = {
        "wa_group": wa_group,
        "area_pk": area_pk,
        "workareas": workareas,
        "order": order,
        "orders": orders,
        "ordertests": ordertests,
        "testgroup": testgroup,
    }
    return render(request, tempate, context)


@login_required(login_url="login_billing")
def show_complete_orders(request):
    workareas = models.Workarea.objects.all().order_by("sort")

    data = models.Orders.objects.filter(status__gte=3)
    # data = models.Orders.objects.all()

    request.GET = request.GET.copy()
    s = request.GET.get("number")
    if s:
        request.GET["number"] = "".join([i for i in s if i.isnumeric()])

    filter = filters.WokareaFilter(request.GET, queryset=data)
    ordertable = tables.CompleteOrderTable(filter.qs)
    ordertable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(ordertable)

    tempate = "corelab/complete.html"
    context = {"workareas": workareas, "ordertable": ordertable, "filter": filter}
    return render(request, tempate, context)


@login_required(login_url="login_billing")
def sample_receive(request):
    orderno = None
    order = None
    samples = None
    order_sample_id = None
    printer = None
    get_sample = False
    receive = False
    request_new = False
    request_new_data = models.RequestNewReasons.objects.all()
    label_printer = models.LabelPrinters.objects.filter(active=True)
    if request.method == "POST":
        orderno = request.POST["orderno"]
        orderno = str(orderno).strip()  # clean
        order = models.Orders.objects.filter(number=orderno)
        samples = models.OrderSamples.objects.filter(order=order)
        for par in request.POST:
            if par == "getsample":
                get_sample = True
            if str(par).startswith("receive_"):
                receive = True
                order_sample_id = str(par).split("_")[1]
                order_sample = models.OrderSamples.objects.get(pk=order_sample_id)
                order_sample.status = 1
                order_sample.lastmodifiedby = request.user
                order_sample.save()
                # log
                order_sample_log = models.OrderSampleLogs(
                    order_sample=order_sample,
                    status=order_sample.status,
                    lastmodifiedby=request.user,
                    lastmodification=timezone.now(),
                )
                order_sample_log.save()
                # order log
                act_txt = (
                    "Sample No. "
                    + order_sample.sample_no
                    + " "
                    + str(_(" received by "))
                    + str(request.user)
                )
                his_order = models.HistoryOrders(
                    order_id=order_sample.order_id,
                    action_code="SAMPLERECEIVED",
                    action_user=str(request.user),
                    action_date=timezone.now(),
                    action_text=act_txt,
                )
                his_order.save()
            if par == "requestnew":
                request_new = True
                reason = request.POST["reason"]
                order_sample_id = request.POST["order_sample_id"]
                order_sample = models.OrderSamples.objects.get(pk=order_sample_id)
                order_sample.status = 2
                order_sample.lastmodifiedby = request.user
                order_sample.save()
                # log
                request_new_reason = models.RequestNewReasons.objects.get(pk=reason)
                order_sample_log = models.OrderSampleLogs(
                    order_sample=order_sample,
                    status=order_sample.status,
                    lastmodifiedby=request.user,
                    lastmodification=timezone.now(),
                    request_new=request_new_reason,
                )
                order_sample_log.save()
                # order log
                act_txt = _("Sample received ") + order_sample.sample_no
                his_order = models.HistoryOrders(
                    order_id=order_sample.order_id,
                    action_code="SAMPLEREQNEW",
                    action_user=str(request.user),
                    action_date=timezone.now(),
                    action_text=act_txt,
                )
                his_order.save()
            if par == "addcomment":
                request_new = True
                comment = request.POST["comment"]
                order_sample_id = request.POST["order_sample_id"]
                order_sample = models.OrderSamples.objects.get(pk=order_sample_id)
                # log
                order_sample_log = models.OrderSampleLogs(
                    order_sample=order_sample,
                    status=0,
                    lastmodifiedby=request.user,
                    lastmodification=timezone.now(),
                    note=comment,
                )
                order_sample_log.save()
                # order log
                act_txt = (
                    _("Sample comment ") + order_sample.sample_no + " : " + comment
                )
                his_order = models.HistoryOrders(
                    order_id=order_sample.order_id,
                    action_code="SAMPLECOMMENT",
                    action_user=str(request.user),
                    action_date=timezone.now(),
                    action_text=act_txt,
                )
                his_order.save()

    else:
        # GET
        # print request.GET
        try:
            printer = request.GET["printer"]
            order_sample_id = request.GET["order_sample_id"]
        except Exception as e:
            pass
        if printer:
            order_sample_id = request.GET["order_sample_id"]
            printer_id = request.GET["printer"]

            o_order_sample = models.OrderSamples.objects.get(pk=order_sample_id)
            order = models.Orders.objects.filter(pk=o_order_sample.order_id)
            o_order = models.Orders.objects.get(pk=o_order_sample.order_id)
            samples = models.OrderSamples.objects.filter(order=o_order)

            orderno = o_order.number

            MESSAGE_TAGS = {messages.ERROR: "danger"}

            printer_id = request.GET.get("printer")

            p_label = Label()
            p_label.set_order_sample_id(order_sample_id)
            p_label.set_labelprinter_id(printer_id)

            not_err, msg = p_label.print_label()

            if not_err:
                messages.info(request, msg)
            else:
                messages.error(
                    request, "Error when printer label [%s]" % msg, extra_tags="danger"
                )

    tempate = "corelab/sample_receive.html"
    context = {
        "orderno": orderno,
        "order": order,
        "samples": samples,
        "request_new_data": request_new_data,
        "label_printer": label_printer,
    }
    return render(request, tempate, context)


@login_required(login_url="login_billing")
def instrument_batch_samples(request, pk):
    inst = models.Instruments.objects.get(pk=pk)
    if request.method == "POST":
        sampleno = request.POST["sampleno"]
        order_sample = models.OrderSamples.objects.filter(sample_no=sampleno)
        for ordsmp in order_sample:
            os = models.OrderSamples.objects.get(pk=ordsmp.id)
            obj, created = models.InstrumentBatch.objects.get_or_create(
                order_sample=os, instrument=inst
            )
            obj.status = 0
            obj.note = None
            obj.save()

    inst_sample = models.InstrumentBatch.objects.filter(instrument=inst)

    instsampletable = tables.InstrumentBachTable(inst_sample)
    instsampletable.paginate(page=request.GET.get("page", 1), per_page=10)

    RequestConfig(request).configure(instsampletable)

    tempate = "corelab/instrumentbatch_samples.html"
    context = {"instrument": inst, "instsampletable": instsampletable}
    return render(request, tempate, context)


# ###################
# ##   Base Views  ##
# ###################


class PaginatedTableView(SingleTableView):
    filter_class = None

    def __init__(self, **kwargs):
        super(PaginatedTableView, self).__init__(**kwargs)
        self.object_list = self.model.objects.all()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        config = RequestConfig(request)
        table = self.table_class(self.object_list)
        config.configure(table)
        table.paginate(page=request.GET.get("page", 1), per_page=self.table_pagination)
        context[self.context_table_name] = table
        return self.render_to_response(context)


class FilteredSingleTableView(SingleTableView):
    filter_class = None

    def get_table_data(self):
        data = super(FilteredSingleTableView, self).get_table_data()
        self.filter = self.filter_class(self.request.GET, queryset=data)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(FilteredSingleTableView, self).get_context_data(**kwargs)
        context["filter"] = self.filter
        return context


class ListTestGroups(
    LoginRequiredMixin, PermissionRequiredMixin, FilteredSingleTableView
):
    model = models.TestGroups
    permission_required = "corelism.view_testgroups"
    login_url = settings.LOGIN_URL_BILLING
    table_class = TestGroupsTable
    table_data = models.TestGroups.objects.all()
    context_table_name = "testgroupstable"
    filter_class = filters.TestGroupFilter
    table_pagination = 10


class CreateTestGroup(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    CreateWithInlinesAndModifiedByMixin,
):
    model = models.TestGroups
    permission_required = "corelism.add_testgroups"
    login_url = settings.LOGIN_URL_BILLING
    fields = ["name", "sort"]
    success_url = reverse_lazy("testgroups_list")


class ViewTestGroup(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.TestGroups
    permission_required = "corelism.view_testgroups"
    login_url = settings.LOGIN_URL_BILLING


class EditTestGroup(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    UpdateWithInlinesAndModifiedByMixin,
):
    model = models.TestGroups
    permission_required = "corelism.change_testgroups"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("testgroups_list")
    form_class = forms.TestGroupForm


class DeleteTestGroup(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.TestGroups
    permission_required = "corelism.delete_testgroups"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("testgroups_list")
    table_pagination = 10


class ListTests(LoginRequiredMixin, PermissionRequiredMixin, FilteredSingleTableView):
    model = models.Tests
    permission_required = "corelism.view_tests"
    login_url = settings.LOGIN_URL_BILLING
    table_class = tables.TestsTable
    table_data = models.Tests.objects.all()
    context_table_name = "teststable"
    filter_class = filters.TestFilter
    table_pagination = 10


class CreateTests(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    CreateWithInlinesAndModifiedByMixin,
):
    model = models.Tests
    permission_required = "corelism.add_tests"
    login_url = settings.LOGIN_URL_BILLING
    fields = ["test_group", "name", "sort"]
    success_url = reverse_lazy("tests_list")


class ViewTests(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Tests
    permission_required = "corelism.view_tests"
    login_url = settings.LOGIN_URL_BILLING


class EditTests(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    UpdateWithInlinesAndModifiedByMixin,
):
    model = models.Tests
    permission_required = "corelism.change_tests"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("tests_list")
    form_class = forms.TestForm


class DeleteTests(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Tests
    permission_required = "corelism.delete_testgroups"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("tests_list")
    table_pagination = 10


class ListOrders(LoginRequiredMixin, PermissionRequiredMixin, FilteredSingleTableView):
    model = models.Orders
    permission_required = "corelism.view_orders"
    login_url = settings.LOGIN_URL_BILLING
    table_class = tables.OrdersTable
    table_data = models.Orders.objects.filter()
    context_table_name = "orderstable"
    filter_class = filters.OrderFilter
    # table_pagination = 10

    def get_context_data(self, **kwargs):
        context = super(ListOrders, self).get_context_data(**kwargs)
        workareas = models.Workarea.objects.all().order_by("sort")
        context["workareas"] = workareas
        return context


class EditOrder(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    UpdateWithInlinesAndModifiedByMixin,
):
    model = models.Orders
    template_name = "corelab/orders_form.html"
    permission_required = "corelism.change_orders"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("orders_list")
    form_class = forms.OrderForm2

    def get_context_data(self, **kwargs):
        context = super(EditOrder, self).get_context_data(**kwargs)
        test_group = (
            models.TestGroups.objects.filter(show_request=True).all().order_by("sort")
        )
        test = models.Tests.objects.filter(can_request=True).all().order_by("sort")
        profile = models.Profile.objects.filter(active=True).all().order_by("sort")
        # print profile
        test_selections = (
            models.Orders.objects.get(id=self.kwargs["pk"])
            .order_items.all()
            .values_list("test_id", flat=True)
            .order_by("id")
        )
        profile_selections = (
            models.Orders.objects.get(id=self.kwargs["pk"])
            .order_items.all()
            .values_list("profile_id", flat=True)
            .order_by("id")
        )
        context["test_group"] = test_group
        context["test"] = test
        context["profile"] = profile
        context["test_selections"] = test_selections
        context["profile_selections"] = profile_selections

        return context

    def post(self, request, *args, **kwargs):
        order = models.Orders.objects.get(number=request.POST["number"])
        form = forms.OrderForm2(request.POST, instance=order)
        test_group = (
            models.TestGroups.objects.filter(show_request=True).all().order_by("sort")
        )
        test = models.Tests.objects.filter(can_request=True).all().order_by("sort")
        profile = models.Profile.objects.filter(active=True).all().order_by("sort")
        # print profile
        test_selections = (
            models.Orders.objects.get(id=self.kwargs["pk"])
            .order_items.all()
            .values_list("test_id", flat=True)
            .order_by("id")
        )
        profile_selections = (
            models.Orders.objects.get(id=self.kwargs["pk"])
            .order_items.all()
            .values_list("profile_id", flat=True)
            .order_by("id")
        )
        # print form.is_valid()
        if form.is_valid():
            form.save()
            tes = models.OrderTests.objects.filter(order=order)
            tes.delete()
            dg = models.OrderDiagnosis.objects.filter(order=order)
            dg.delete()
            # print form
            for test in form.cleaned_data["test_selections"]:
                # print test
                order_item = models.OrderTests()
                order_item.order = order
                order_item.test = test
                # print type(test)
                order_item.save()
            for profile in form.cleaned_data["profile_selections"]:
                profile_test = models.ProfileTests.objects.filter(profile=profile)
                # print profile_test
                for test in profile_test:
                    # print test.test_id
                    tes = models.OrderTests.objects.filter(
                        order=order, test_id=test.test_id
                    )
                    tes.delete()
                    order_item = models.OrderTests()
                    order_item.order = order
                    order_item.test = models.Tests.objects.get(pk=test.test_id)
                    order_item.profile = profile
                    order_item.save()

            for diagnosis in form.cleaned_data["diagnosis_selections"]:
                order_diagitems = models.OrderDiagnosis()
                order_diagitems.order = order
                order_diagitems.diagnosis = diagnosis
                order_diagitems.save()
            return redirect("order_detail", pk=order.pk)
        else:
            messages.error(request, "Error")

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "test_group": test_group,
                "test": test,
                "profile": profile,
                "test_selections": test_selections,
                "profile_selections": profile_selections,
            },
        )


class ViewOrder(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Orders
    permission_required = "corelism.view_orders"
    login_url = settings.LOGIN_URL_BILLING

    def get_context_data(self, **kwargs):
        context = super(ViewOrder, self).get_context_data(**kwargs)
        context["samples"] = models.OrderSamples.objects.filter(
            order_id=self.kwargs["pk"]
        )
        context["labelprinters"] = models.LabelPrinters.objects.filter(active=True)
        context["MENU_BTN_PRINT_RECEIPT"] = models.Parameters.objects.filter(
            name="MENU_BTN_PRINT_RECEIPT"
        )[0]
        context["MENU_BTN_PRINT_BILL"] = models.Parameters.objects.filter(
            name="MENU_BTN_PRINT_BILL"
        )[0]
        context["MENU_BTN_PRINT_BARCODE"] = models.Parameters.objects.filter(
            name="MENU_BTN_PRINT_BARCODE"
        )[0]
        return context


class DeleteOrder(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Orders
    permission_required = "corelism.delete_order"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("orders_list")
    table_pagination = 10


class ListPatients(
    LoginRequiredMixin, PermissionRequiredMixin, FilteredSingleTableView
):
    model = models.Patients
    permission_required = "corelab.view_patients"
    # login_url = settings.LOGIN_URL_BILLING
    table_class = PatientsTable
    table_data = models.Patients.objects.all()
    context_table_name = "patientstable"
    filter_class = filters.PatientFilter
    # table_pagination = 10


class CreatePatient(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    CreateWithInlinesView,
):
    model = models.Patients
    permission_required = "corelism.add_patients"
    login_url = settings.LOGIN_URL_BILLING
    fields = [
        "patient_id",
        "name",
        "gender",
        "dob",
        "address",
    ]
    success_url = reverse_lazy("patients_list")


class ViewPatients(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Patients
    permission_required = "corelism.view_patients"
    login_url = settings.LOGIN_URL_BILLING

    def get_context_data(self, **kwargs):
        context = super(ViewPatients, self).get_context_data(**kwargs)
        context["visit"] = (
            models.Orders.objects.filter(
                patient_id=self.kwargs["pk"], number__isnull=False
            )
            .values("origin__name", "origin__id", "insurance__name", "insurance__id")
            .annotate(Count("number"))
            .order_by("origin__name", "insurance__name")
        )
        # print context['visit'].query
        return context


class EditPatient(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    UpdateWithInlinesAndModifiedByMixin,
):
    model = models.Patients
    permission_required = "corelism.change_patient"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("patients_list")
    form_class = forms.PatientForm


class DeletePatient(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Patients
    permission_required = "corelism.delete_patient"
    login_url = settings.LOGIN_URL_BILLING
    success_url = reverse_lazy("patients_list")
    table_pagination = 10


class Listjm(LoginRequiredMixin, PermissionRequiredMixin, FilteredSingleTableView):
    model = models.Orders
    permission_required = "corelism.view_patients"
    login_url = settings.LOGIN_URL_BILLING
    table_class = JMTable
    table_data = models.Orders.objects.all()
    context_table_name = "patientstable"
    filter_class = filters.JMFilter
    # table_pagination = 10


class ListWorklists(
    LoginRequiredMixin, PermissionRequiredMixin, FilteredSingleTableView
):
    model = models.Worklists
    permission_required = "corelism.view_wokrlists"
    login_url = settings.LOGIN_URL_BILLING
    table_class = WorklistTable
    table_data = models.Worklists.objects.all()
    context_table_name = "worklisttable"
    filter_class = filters.WorklistFilter
    # table_pagination = 10


class CreateWorklist(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    NamedFormsetsMixin,
    CreateWithInlinesAndModifiedByMixin,
):
    model = models.Worklists
    permission_required = "corelism.add_worklists"
    login_url = settings.LOGIN_URL_BILLING
    fields = ["batch_group"]
    success_url = reverse_lazy("worklists_list")

    def form_valid(self, form):
        form.lastmodifiedby = self.request.user
        return super().form_valid(form)


class ViewWorklist(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Worklists
    permission_required = "corelism.view_worklists"
    login_url = settings.LOGIN_URL_BILLING


class ListInstrumentBatchMode(
    LoginRequiredMixin, PermissionRequiredMixin, FilteredSingleTableView
):
    model = models.Instruments
    permission_required = "corelism.view_instruments"
    login_url = settings.LOGIN_URL_BILLING
    table_class = InstrumentBachModeTable
    table_data = models.Instruments.objects.filter(batch_mode=True)
    template_name = "about.html"
    context_table_name = "instrumentbatchmodetable"
    filter_class = filters.TestGroupFilter
    # table_pagination = 10


################### API #############################
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response(
            {"error": "Please provide both username and password"},
            status=HTTP_400_BAD_REQUEST,
        )
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "Invalid Credentials"}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def api_test(request):
    data = {"sample_data": 123}
    return Response(data, status=HTTP_200_OK)


############ REPORT ###################
@csrf_exempt
@api_view(["GET"])
def pbs_report(request, pk):
    order = models.Orders.objects.get(pk=pk)
    group_id = request.GET.get("group_id")

    input_file_header = settings.RESULT_REPORT_FILE_HEADER
    input_file_footer = settings.RESULT_REPORT_FILE_FOOTER
    input_file_main = settings.RESULT_REPORT_FILE_MAIN
    input_file = settings.RESULT_REPORT_FILE

    ts = datetime.today().strftime("%Y%m%d%H%M%S")
    parameters = {"ORDER_ID": pk}
    output = settings.MEDIA_ROOT + "\\report\\" + str(order.number) + "_" + ts + ".pdf"
    con = settings.JASPER_CONN

    res_rep = report.JasperServer()

    b_ok, content = res_rep.get_report_order(pk, "PBSReport", "pdf")

    # print b_ok

    # print content

    if b_ok:
        fd = open(output, "wb")
        fd.write(content)
        fd.close()

        base_url = request.build_absolute_uri("/")[:-1].strip("/")
        url_pdf = base_url + "/media/report/" + str(order.number) + "_" + ts + ".pdf"

        # save report URL
        oe, _created = models.OrderExtended.objects.get_or_create(order_id=pk)

        oe.result_pdf_url = url_pdf
        oe.save()

        # set validation printed
        if request.user.is_authenticated():
            order_res = models.OrderResults.objects.filter(
                order_id=pk, validation_status=3
            ).update(
                validation_status=4,
                print_user=str(request.user),
                print_date=timezone.now(),
            )

        template = "middleware/result_pdf_preview.html"
        context = {"order": order, "url_pdf": url_pdf}
        return render(request, template, context)
    else:
        return JsonResponse(content)


@csrf_exempt
@api_view(["GET"])
def mb_report(request, pk):
    order = models.Orders.objects.get(pk=pk)

    group_id = request.GET.get("group_id")

    input_file_header = settings.RESULT_REPORT_FILE_HEADER
    input_file_footer = settings.RESULT_REPORT_FILE_FOOTER
    input_file_main = settings.RESULT_REPORT_FILE_MAIN
    input_file = settings.RESULT_REPORT_FILE

    ts = datetime.today().strftime("%Y%m%d%H%M%S")
    parameters = {"ORDER_ID": pk}
    output = settings.MEDIA_ROOT + "\\report\\" + str(order.number) + "_" + ts + ".pdf"
    con = settings.JASPER_CONN

    res_rep = report.JasperServer()

    b_ok, content = res_rep.get_report_order(pk, "MBReport", "pdf")

    # print b_ok

    # print content

    if b_ok:
        fd = open(output, "wb")
        fd.write(content)
        fd.close()

        base_url = request.build_absolute_uri("/")[:-1].strip("/")
        url_pdf = base_url + "/media/report/" + str(order.number) + "_" + ts + ".pdf"

        # save report URL
        oe, _created = models.OrderExtended.objects.get_or_create(order_id=pk)

        oe.result_pdf_url = url_pdf
        oe.save()

        # set validation printed
        if request.user.is_authenticated():
            order_res = models.OrderResults.objects.filter(
                order_id=pk, validation_status=3
            ).update(
                validation_status=4,
                print_user=str(request.user),
                print_date=timezone.now(),
            )

        template = "middleware/result_pdf_preview.html"
        context = {"order": order, "url_pdf": url_pdf}
        return render(request, template, context)
    else:
        return JsonResponse(content)


class OrderListViewSet(generics.ListAPIView):
    queryset = models.Orders.objects.all()
    serializer_class = OrdersSerializer
    filter_backends = (resfilters.SearchFilter,)
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


########### AJAX CALL ########################


@login_required(login_url="login_billing")
def json_pervious_result(request, order_pk, test_pk):
    order = models.Orders.objects.get(pk=order_pk)
    test = models.Tests.objects.get(pk=test_pk)
    order_result = (
        models.OrderResults.objects.filter(
            order_id__lt=order_pk,
            order__patient_id=order.patient_id,
            test=test,
            validation_status__gte=3,
        )
        .values("id", "order__number", "order__order_date", "result__alfa_result")
        .order_by("-order_id")
    )
    return JsonResponse({"results": list(order_result)})


@login_required(login_url="login_billing")
def json_sample_receive(request, order_pk):
    order = models.Orders.objects.get(pk=order_pk)
    order_sample = (
        models.OrderSamples.objects.filter(order=order)
        .values("id", "sample_no", "specimen__name", "status")
        .order_by("id")
    )
    l_order_sample = list(order_sample)
    sample_status = models.SAMPLE_STATUS
    for l_os in l_order_sample:
        for key, value in sample_status:
            if l_os["status"] == key:
                l_os["status_display"] = value
                l_os["log"] = wa_status.order_sample_log(l_os["id"])
    return JsonResponse({"results": list(order_sample)})
