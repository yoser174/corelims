from __future__ import unicode_literals

from django.urls import re_path, include
from rest_framework import routers
from . import views, models, serializers

# Router setup
router = routers.DefaultRouter()
router.register(r"orders", views.OrderViewSet)
router.register(r"patients", views.PatientViewSet)
router.register(r"doctors", views.DoctorViewSet)
router.register(r"origins", views.OriginViewSet)
router.register(r"insurances", views.InsuranceViewSet)
router.register(r"results", views.ResultViewSet)

# URL patterns
urlpatterns = [
    # Home and authentication
    re_path(r"^$", views.home, name="home_billing"),
    re_path(r"^dashboard/$", views.show_dashboard, name="dashboard_billing"),
    re_path(r"^login/$", views.login_user, name="login_billing"),
    re_path(r"^logout/$", views.login_user, name="logout_billing"),
    re_path(r"^avatarchange/$", views.AvatarChange, name="avatar_change_billing"),
    re_path(r"^avataradd/$", views.AvatarAdd, name="avatar_add_billing"),
    re_path(
        r"^profileupdate/(?P<pk>\d+)/$",
        views.UpdateUserProfile,
        name="profile_update_billing",
    ),
    # Test Groups
    re_path(r"^testgroups/$", views.ListTestGroups.as_view(), name="testgroups_list"),
    re_path(
        r"^testgroups/detail/(?P<pk>\d+)/$",
        views.ListTestGroups.as_view(),
        name="testgroups_detail",
    ),
    re_path(
        r"^testgroups/create/$",
        views.CreateTestGroup.as_view(),
        name="testgroups_create",
    ),
    re_path(
        r"^testgroups/edit/(?P<pk>\d+)/$",
        views.EditTestGroup.as_view(),
        name="testgroups_edit",
    ),
    re_path(
        r"^testgroups/delete/(?P<pk>\d+)/$",
        views.DeleteTestGroup.as_view(),
        name="testgroups_delete",
    ),
    # Tests
    re_path(r"^tests/$", views.ListTests.as_view(), name="tests_list"),
    re_path(
        r"^tests/detail/(?P<pk>\d+)/$", views.ListTests.as_view(), name="tests_detail"
    ),
    re_path(r"^tests/create/$", views.CreateTests.as_view(), name="tests_create"),
    re_path(r"^tests/edit/(?P<pk>\d+)/$", views.EditTests.as_view(), name="tests_edit"),
    re_path(
        r"^tests/delete/(?P<pk>\d+)/$", views.DeleteTests.as_view(), name="tests_delete"
    ),
    # Orders
    re_path(r"^orders/$", views.ListOrders.as_view(), name="orders_list"),
    re_path(
        r"^orders/edit/(?P<pk>\d+)/$", views.EditOrder.as_view(), name="order_edit"
    ),
    re_path(r"^orders/patient/$", views.order_patient, name="order_patient"),
    re_path(
        r"^orders/delete/(?P<pk>\d+)/$",
        views.DeleteOrder.as_view(),
        name="order_delete",
    ),
    re_path(
        r"^orders/add/patient/$", views.order_add_patient, name="order_add_patient"
    ),
    re_path(
        r"^orders/patient/create/(?P<patient_pk>\d+)/$",
        views.create_order_from_patient,
        name="create_order_from_patient",
    ),
    re_path(
        r"^orders/detail/(?P<pk>\d+)/$", views.ViewOrder.as_view(), name="order_detail"
    ),
    re_path(
        r"^orders/detail/(?P<order_pk>\d+)/print/receipt$",
        views.order_print_receipt,
        name="order_print_receipt",
    ),
    re_path(
        r"^orders/detail/(?P<order_pk>\d+)/print/bill$",
        views.order_print_bill,
        name="order_print_bill",
    ),
    re_path(
        r"^orders/detail/(?P<order_pk>\d+)/print/worklist$",
        views.order_print_worklist,
        name="order_print_worklist",
    ),
    re_path(
        r"^orders/detail/(?P<order_pk>\d+)/label$",
        views.order_print_barcode,
        name="order_barcode",
    ),
    re_path(
        r"^orders/detail/(?P<order_pk>\d+)/send/lis$",
        views.order_send_lis,
        name="order_send_lis",
    ),
    # Patients
    re_path(r"^patients/$", views.ListPatients.as_view(), name="patients_list"),
    re_path(
        r"^patients/detail/(?P<pk>\d+)/$",
        views.ViewPatients.as_view(),
        name="patient_detail",
    ),
    re_path(
        r"^patients/create/$", views.CreatePatient.as_view(), name="patient_create"
    ),
    re_path(
        r"^patients/edit/(?P<pk>\d+)/$",
        views.EditPatient.as_view(),
        name="patient_edit",
    ),
    re_path(
        r"^patients/delete/(?P<pk>\d+)/$",
        views.DeletePatient.as_view(),
        name="patient_delete",
    ),
    re_path(
        r"^patients/bill-report/(?P<pk>\d+)/$",
        views.patient_print_bill,
        name="patient_bill_report",
    ),
    re_path(
        r"^patients/trans_history/(?P<pk>\d+)/$",
        views.patient_trans_history,
        name="patient_trans_history",
    ),
    re_path(
        r"^patients/trans_history/perview/(?P<pk>\d+)/$",
        views.patient_trans_history_perview,
        name="patient_trans_history_perview",
    ),
    # Sample Receive
    re_path(r"^sample_receive/$", views.sample_receive, name="sample_receive"),
    re_path(
        r"^sample_receive/label/$",
        views.order_sample_label,
        name="sample_receive_label",
    ),
    # Instrument Batch
    re_path(
        r"^instrument_batch/$",
        views.ListInstrumentBatchMode.as_view(),
        name="instrument_batch",
    ),
    re_path(
        r"^instrument_batch/(?P<pk>\d+)/$",
        views.instrument_batch_samples,
        name="instrument_batch_list",
    ),
    # Worklists
    re_path(r"^worklists/$", views.ListWorklists.as_view(), name="worklists_list"),
    re_path(
        r"^worklists/create/$", views.CreateWorklist.as_view(), name="worklist_create"
    ),
    re_path(
        r"^worklists/detail/(?P<pk>\d+)/$",
        views.ViewWorklist.as_view(),
        name="worklist_detail",
    ),
    re_path(
        r"^worklists/detail/(?P<pk>\d+)/print$",
        views.worklist_print,
        name="worklist_print",
    ),
    #################
    # Order Results
    #################
    re_path(r"^workarea/$", views.show_workarea, name="workarea"),
    re_path(
        r"^orders/results/(?P<pk>\d+)/$", views.order_results, name="order_results"
    ),
    # url(r'^orders/results/(?P<pk>\d+)/validate/$', views.order_results_validate, name='order_results_validate'),
    re_path(
        r"^orders/results/(?P<pk>\d+)/techval/$",
        views.order_results_techval,
        name="order_results_techval",
    ),
    re_path(
        r"^orders/results/(?P<pk>\d+)/medval/$",
        views.order_results_medval,
        name="order_results_medval",
    ),
    re_path(
        r"^orders/results/(?P<pk>\d+)/print/$",
        views.order_results_print,
        name="order_results_print",
    ),
    re_path(
        r"^orders/results/(?P<pk>\d+)/repeat/$",
        views.order_results_repeat,
        name="order_results_repeat",
    ),
    re_path(
        r"^orders/results/(?P<pk>\d+)/history/$",
        views.order_results_history,
        name="order_results_history",
    ),
    re_path(
        r"^orders/results/(?P<pk>\d+)/print_draft/$",
        views.order_result_print_draft,
        name="order_results_print_draft",
    ),
    re_path(
        r"^orders/resultreport/(?P<pk>\d+)/$",
        views.order_result_report,
        name="order_results_report",
    ),
    #################
    # Workareas
    #################
    re_path(
        r"^workarea/(?P<pk>\d+)/$", views.show_workarea_group, name="workarea_group"
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/$",
        views.order_results_wa,
        name="order_results_wa",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/techval/$",
        views.order_results_techval,
        name="order_results_techval_wa",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/capture/$",
        views.capture_workarea,
        name="capture_workarea",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/medval/$",
        views.order_results_medval,
        name="order_results_medval_wa",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/print/$",
        views.order_results_print_wa,
        name="order_results_print_wa",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/repeat/$",
        views.order_results_repeat,
        name="order_results_repeat_wa",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/history/$",
        views.workarea_order_results_history,
        name="workarea_order_results_history",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/print_draft/$",
        views.order_result_print_draft,
        name="order_results_print_draft_wa",
    ),
    re_path(
        r"^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/$",
        views.order_result_report,
        name="order_results_report_wa",
    ),
    # Quality Control
    re_path(
        r"^quality_control/$", views.QualityControl.as_view(), name="quality_control"
    ),
    re_path(
        r"^quality_control/create/$",
        views.CreateQualityControl.as_view(),
        name="qualitycontrol_create",
    ),
    #################
    # Complete orders
    #################
    re_path(r"^complete/$", views.show_complete_orders, name="complete_orders"),
    re_path(
        r"^complete/results/(?P<pk>\d+)/$",
        views.complete_results,
        name="complete_results",
    ),
    re_path(
        r"^complete/results/(?P<pk>\d+)/print/$",
        views.order_results_print,
        name="order_results_print",
    ),
    re_path(
        r"^complete/results/(?P<pk>\d+)/repeat/$",
        views.order_results_repeat,
        name="order_results_repeat",
    ),
    re_path(
        r"^complete/results/(?P<pk>\d+)/history/$",
        views.order_results_history,
        name="order_results_history",
    ),
    re_path(
        r"^complete/results/(?P<pk>\d+)/print_draft/$",
        views.order_result_print_draft,
        name="order_results_print_draft",
    ),
    re_path(
        r"^complete/resultreport/(?P<pk>\d+)/$",
        views.order_result_report,
        name="order_results_report",
    ),
    # Reports
    re_path(r"^reports/orders/$", views.report_orders, name="rep_orders_list"),
    re_path(
        r"^reports/ordertests/$", views.report_ordertests, name="rep_ordertests_list"
    ),
    re_path(r"^reports/tats/$", views.report_tats, name="rep_tat"),
    re_path(r"^reports/jm/$", views.report_jm, name="jm_list"),
    re_path(r"^reports/origin/$", views.report_origin, name="origin_list"),
    re_path(r"^reports/insurance/$", views.report_insurance, name="insurance_list"),
    re_path(r"^reports/tests/$", views.report_tests, name="tests_list"),
    re_path(
        r"^reports/inpatmedsrv/$", views.report_inpatmedsrv, name="inpatmedsrv_list"
    ),
    # API
    re_path(r"^api/", include(router.urls)),
    re_path(r"^api/login/$", views.api_login, name="api_login"),
    re_path(r"^api/test/$", views.api_test, name="api_test"),
    re_path(r"^api/mb_report/(?P<pk>\d+)/$", views.mb_report, name="mb_report"),
    re_path(r"^api/pbs_report/(?P<pk>\d+)/$", views.pbs_report, name="pbs_report"),
    re_path(
        r"^api/orders/$",
        views.OrderListViewSet.as_view(
            queryset=models.Orders.objects.all(),
            serializer_class=serializers.OrdersSerializer,
        ),
        name="order-list",
    ),
    # JSON
    re_path(
        r"^json/pervious_results/(?P<order_pk>\d+)/(?P<test_pk>\d+)/$",
        views.json_pervious_result,
        name="json_pervious_result",
    ),
    re_path(
        r"^json/sample_receive/(?P<order_pk>\d+)/$",
        views.json_sample_receive,
        name="json_sample_receive",
    ),
    # Avatar
    re_path(r"^avatar/", include("avatar.urls")),
    # json
    re_path(r"^chart_data/", views.qc_data, name="qc_data"),
]
