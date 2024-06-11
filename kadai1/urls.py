from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('doctor_home/', views.doctor_home, name='doctor_home'),
    path('reception_home/', views.reception_home, name='reception_home'),
    path('admin_home/register/', views.register_view, name='register'),
    path('admin_home/register/complete/', views.register_complete, name='register_complete'),
    path('admin_home/namechange/', views.namechange_view, name='namechange'),
    path('admin_home/namechange_success/', views.namechange_success, name='namechange_success'),
    path('admin_home/ohregister/', views.other_hospital_register_view, name='ohregister'),
    path('admin_home/other_hospitals/', views.other_hospital_list, name='otherhospitallist'),
    path('admin_home/other_hospital_search/', views.search_hospital_by_address, name='otherhospitalsearch'),
    path('reception_home/passchange/', views.change_password_view, name='passchange'),
    path('patient_register/', views.patient_register_view, name='patient_register'),
    path('patient_register_confirm/', views.patient_register_confirm_view, name='patient_register_confirm'),
    path('insurance_card_change/', views.insurance_card_change_view, name='insurance_card_change'),
    path('insurance_card_change_confirm/', views.insurance_card_change_confirm_view, name='insurance_card_change_confirm'),
    path('search_patient_by_id/', views.search_patient_by_id, name='search_patient_by_id'),
    path('search_patient_by_name/', views.search_patient_by_name, name='patient_name_search'),
    path('medication_instruction/<str:patient_id>/', views.medication_instruction, name='medication_instruction'),
    path('medication_confirmation/', views.medication_confirmation, name='medication_confirmation'),
    path('treatment_history/', views.treatment_history, name='treatment_history'),

]
