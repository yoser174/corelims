from __future__ import unicode_literals

from django.conf.urls import  url,include
from rest_framework import routers
from . import views,models,serializers

router = routers.DefaultRouter()
router.register(r'orders', views.OrderViewSet)
router.register(r'patients', views.PatientViewSet)
router.register(r'doctors', views.DoctorViewSet)
router.register(r'origins', views.OriginViewSet)
router.register(r'insurances', views.InsuranceViewSet)
router.register(r'results', views.ResultViewSet)



urlpatterns = [
    
    url("^$", views.home, name="home_billing"),
    url(r'^dashboard/$', views.show_dashboard, name='dashboard_billing'),
    url(r'^login/$', views.login_user, name='login_billing'),
    url(r'^logout/$', views.login_user, name='logout_biling'),
    url(r'^avatarchange/$', views.AvatarChange, name='avatar_change_billing'),
    url(r'^avataradd/$', views.AvatarAdd, name='avatar_add_billing'),
    
    url(r'^profileupdate/(?P<pk>\d+)/$', views.UpdateUserProfile, name='profile_update_billing'),
    
    # #############
    # Test Groups urls
    # #############
    url(r'^testgroups/$', views.ListTestGroups.as_view(), name='testgroups_list'),
    url(r'^testgroups/detail/(?P<pk>\d+)/$', views.ListTestGroups.as_view(), name='testgroups_detail'),
    url(r'^testgroups/create/$', views.CreateTestGroup.as_view(), name='testgroups_create'),
    url(r'^testgroups/edit/(?P<pk>\d+)/$', views.EditTestGroup.as_view(), name='testgroups_edit'),
    url(r'^testgroups/delete/(?P<pk>\d+)/$', views.DeleteTestGroup.as_view(), name='testgroups_delete'),
    
    # #############
    # Tests urls
    # #############
    url(r'^tests/$', views.ListTests.as_view(), name='tests_list'),
    url(r'^tests/detail/(?P<pk>\d+)/$', views.ListTests.as_view(), name='tests_detail'),
    url(r'^tests/create/$', views.CreateTests.as_view(), name='tests_create'),
    url(r'^tests/edit/(?P<pk>\d+)/$', views.EditTests.as_view(), name='tests_edit'),
    url(r'^tests/delete/(?P<pk>\d+)/$', views.DeleteTests.as_view(), name='tests_delete'),
    
    # #############
    # Order urls
    # #############
    url(r'^orders/$', views.ListOrders.as_view(), name='orders_list'),
    url(r'^orders/edit/(?P<pk>\d+)/$', views.EditOrder.as_view(), name='order_edit'),
    url(r'^orders/patient/$', views.order_patient, name='order_patient'),
    url(r'^orders/delete/(?P<pk>\d+)/$', views.DeleteOrder.as_view(), name='order_delete'),
    url(r'^orders/add/patient/$', views.order_add_patient, name='order_add_patient'),
    url(r'^orders/patient/create/(?P<patient_pk>\d+)/$', views.create_order_from_patient, name='create_order_from_patient'),
    url(r'^orders/detail/(?P<pk>\d+)/$', views.ViewOrder.as_view(), name='order_detail'),
    url(r'^orders/detail/(?P<order_pk>\d+)/print/receipt$', views.order_print_receipt, name='order_print_receipt'),
    url(r'^orders/detail/(?P<order_pk>\d+)/print/bill$', views.order_print_bill, name='order_print_bill'),
    url(r'^orders/detail/(?P<order_pk>\d+)/print/worklist$', views.order_print_worklist, name='order_print_worklist'),
    url(r'^orders/detail/(?P<order_pk>\d+)/label', views.order_print_barcode, name='order_barcode'),
    url(r'^orders/detail/(?P<order_pk>\d+)/send/lis$', views.order_send_lis, name='order_send_lis'),
    
    # #############
    # Patient urls
    # #############
    url(r'^patients/$', views.ListPatients.as_view(), name='patients_list'),
    url(r'^patients/detail/(?P<pk>\d+)/$', views.ViewPatients.as_view(), name='patient_detail'),
    url(r'^patients/create/$', views.CreatePatient.as_view(), name='patient_create'),
    url(r'^patients/edit/(?P<pk>\d+)/$', views.EditPatient.as_view(), name='patient_edit'),
    url(r'^patients/delete/(?P<pk>\d+)/$', views.DeletePatient.as_view(), name='patient_delete'),
    url(r'^patients/bill-report/(?P<pk>\d+)/$', views.patient_print_bill, name='patient_bill_report'),
    url(r'^patients/trans_history/(?P<pk>\d+)/$', views.patient_trans_history, name='patient_trans_history'),
    url(r'^patients/trans_history/perview/(?P<pk>\d+)/$', views.patient_trans_history_perview, name='patient_trans_history_perview'),
    
    #################
    # Sample Receive
    #################
    url(r'^sample_receive/$', views.sample_receive, name='sample_receive'),
    url(r'^sample_receive/label/', views.order_sample_label, name='sample_receive_label'),
    
    #################
    # Intrument batch
    #################
    url(r'^instrument_batch/$', views.ListInstrumentBatchMode.as_view(), name='instrument_batch'),
    url(r'^instrument_batch/(?P<pk>\d+)/', views.instrument_batch_samples, name='instrument_batch_list'),

    
    #################
    # Worklist
    #################
    url(r'^worklists/$', views.ListWorklists.as_view(), name='worklists_list'),
    url(r'^worklists/create/$', views.CreateWorklist.as_view(), name='worklist_create'),
    url(r'^worklists/detail/(?P<pk>\d+)/$', views.ViewWorklist.as_view(), name='worklist_detail'),
    url(r'^worklists/detail/(?P<pk>\d+)/print$', views.worklist_print, name='worklist_print'),
    
    #################
    # Order Results
    #################
    url(r'^workarea/$', views.show_workarea, name='workarea'),
    url(r'^orders/results/(?P<pk>\d+)/$', views.order_results, name='order_results'),
    #url(r'^orders/results/(?P<pk>\d+)/validate/$', views.order_results_validate, name='order_results_validate'),
    url(r'^orders/results/(?P<pk>\d+)/techval/$', views.order_results_techval, name='order_results_techval'),
    url(r'^orders/results/(?P<pk>\d+)/medval/$', views.order_results_medval, name='order_results_medval'),
    url(r'^orders/results/(?P<pk>\d+)/print/$', views.order_results_print, name='order_results_print'),
    url(r'^orders/results/(?P<pk>\d+)/repeat/$', views.order_results_repeat, name='order_results_repeat'),
    url(r'^orders/results/(?P<pk>\d+)/history/$', views.order_results_history, name='order_results_history'),
    url(r'^orders/results/(?P<pk>\d+)/print_draft/$', views.order_result_print_draft, name='order_results_print_draft'),
    url(r'^orders/resultreport/(?P<pk>\d+)/$', views.order_result_report, name='order_results_report'),
    
    #################
    # Workareas
    #################
    url(r'^workarea/(?P<pk>\d+)/$', views.show_workarea_group, name='workarea_group'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/$', views.order_results_wa, name='order_results_wa'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/techval/$', views.order_results_techval, name='order_results_techval_wa'),
    url(r'^workarea/(?P<area_pk>\d+)/capture/$', views.capture_workarea, name='capture_workarea'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/medval/$', views.order_results_medval, name='order_results_medval_wa'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/print/$', views.order_results_print_wa, name='order_results_print_wa'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/repeat/$', views.order_results_repeat, name='order_results_repeat_wa'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/history/$', views.workarea_order_results_history, name='workarea_order_results_history'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/print_draft/$', views.order_result_print_draft, name='order_results_print_draft_wa'),
    url(r'^workarea/(?P<area_pk>\d+)/(?P<order_pk>\d+)/$', views.order_result_report, name='order_results_report_wa'),
    
    
    #################
    # Complete orders
    #################
    url(r'^complete/$', views.show_complete_orders, name='complete_orders'),
    url(r'^complete/results/(?P<pk>\d+)/$', views.complete_results, name='complete_results'),
    url(r'^complete/results/(?P<pk>\d+)/print/$', views.order_results_print, name='order_results_print'),
    url(r'^complete/results/(?P<pk>\d+)/repeat/$', views.order_results_repeat, name='order_results_repeat'),
    url(r'^complete/results/(?P<pk>\d+)/history/$', views.order_results_history, name='order_results_history'),
    url(r'^complete/results/(?P<pk>\d+)/print_draft/$', views.order_result_print_draft, name='order_results_print_draft'),
    url(r'^complete/resultreport/(?P<pk>\d+)/$', views.order_result_report, name='order_results_report'),

    
     # #############
    # Report urls
    # #############
    url(r'^reports/orders/$', views.report_orders, name='rep_orders_list'),
    url(r'^reports/ordertests/$', views.report_ordertests, name='rep_ordertests_list'),
    # old
    url(r'^reports/jm/$', views.report_jm, name='jm_list'),
    url(r'^reports/origin/$', views.report_origin, name='origin_list'),
    url(r'^reports/insurance/$', views.report_insurance, name='insurance_list'),
    url(r'^reports/tests/$', views.report_tests, name='tests_list'),
     url(r'^reports/inpatmedsrv/$', views.report_inpatmedsrv, name='inpatmedsrv_list'),
    
    url(r'^avatar/', include('avatar.urls')),
    
    
    ##################
    # API
    #################
    url(r'^api/', include(router.urls)),
    url(r'^api/login/$', views.api_login, name='api_login'),
    url(r'^api/test/$', views.api_test, name='api_test'),
    url(r'^api/mb_report/(?P<pk>\d+)/$', views.mb_report, name='mb_report'),
    url(r'^api/pbs_report/(?P<pk>\d+)/$', views.pbs_report, name='pbs_report'),
    url(r'^api/orders/', views.OrderListViewSet.as_view(queryset=models.Orders.objects.all(), serializer_class=serializers.OrdersSerializer), name='order-list'),
    
    
    ##################
    # JSON
    ##################
    url(r'^json/pervious_results/(?P<order_pk>\d+)/(?P<test_pk>\d+)/$', views.json_pervious_result, name='json_pervious_result'),
    url(r'^json/sample_receive/(?P<order_pk>\d+)/$', views.json_sample_receive, name='json_sample_receive'),
    ]