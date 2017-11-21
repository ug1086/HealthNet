from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # 127.0.0.1/healthnet/index
    url(r'^index', views.index, name='index'),
    # 127.0.0.1/healthnet/index
    url(r'^appointments/', views.appointments, name='appointments'),
    # 127.0.0.1/healthnet/appointments/
    url(r'^create_appointment/$', views.create_appointment, name='create_appointment'),
    # 127.0.0.1/healthnet/create_appointment/
    url(r'^view_appointment/(?P<appointment_id>[0-9]+)/$', views.view_appointment, name='view_appointment'),
    # 127.0.0.1/healthnet/view_appointment/1/
    url(r'^update_appointment/(?P<appointment_id>[0-9]+)/$', views.update_appointment, name='update_appointment'),
    # 127.0.0.1/healthnet/update_appointment/1/
    url(r'^hospital_admin_index/', views.hospital_admin_index, name="hospital_admin_index"),
    # 127.0.0.1/healthnet/hospital_admin_index/
    url(r'^hospital_admin/create_user', views.hospital_admin_create_user, name="hospital_admin/create_user/"),
    # 127.0.0.1/healthnet/hospital_admin/create_user/
    url(r'^hospital_admin/view_logs/', views.hospital_admin_view_logs, name="hospital_admin/view_logs/"),
    # 127.0.0.1/healthnet/hospital_admin/view_logs/
    url(r'^edit_profile_information/(?P<user_id>[0-9]+)/$', views.edit_profile_information, name="edit_profile_information"),
    # 127.0.0.1/healthnet/edit_profile_information/1/
    url(r'^Appointment', views.Appointment, name='Appointment'),
    # 127.0.0.1/healthnet/Appointment
    url(r'^register', views.register, name='register'),
    # 127.0.0.1/healthnet/register
    url(r'^Login', views.user_login, name='Login'),
    # 127.0.0.1/healthnet/Login
    url(r'^Logout', views.user_logout, name='Logout'),
    # 127.0.0.1/healthnet/Logout
    url(r'^hospital_admin_create_user_success', views.hospital_admin_create_user_success, name="hospital_admin_create_user_success"),
    # 127.0.0.1/healthnet/hospital_admin_create_user_success
    url(r'^login/invalid_login', views.invalid_login, name="invalid_login"),
    # 127.0.0.1/healthnet/login/invalid_login
    url(r'^delete_appointment/(?P<appointment_id>[0-9]+)/$', views.delete_appointment, name="delete_appointment"),
    # 127.0.0.1/healthnet/delete_appointment/1
    url(r'^change_password/(?P<user_id>[0-9]+)/$', views.change_password, name="change_password"),
    # 127.0.0.1/healthnet/change_password/1
    url(r'^invalid_password_change_1', views.invalid_password_change_1, name="invalid_password_change_1"),
    # 127.0.0.1/healthnet/invalid_password_change_1
    url(r'invalid_password_change_2', views.invalid_password_change_2, name="invalid_password_change_2"),
    # 127.0.0.1/healthnet/invalid_password_change_2
    url(r'hospital_admin_create_user_failure', views.hospital_admin_create_user_failure, name="hospital_admin_create_user_failure"),
    # 127.0.0.1/healthnet/hospital_admin_create_user_failure
    url(r'edit_profile_information_failure', views.edit_profile_information_failure, name="edit_profile_information_failure"),
    # 127.0.0.1/healthnet/edit_profile_information_failure
    url(r'hospital_admin_view_logs_create_filters', views.hospital_admin_view_logs_create_filters, name="hospital_admin_view_logs_create_filters"),
    # 127.0.0.1/healthnet/hospital_admin_view_logs_create_filters
    url(r'hospital_admin_view_logs_choose_filters', views.hospital_admin_view_logs_create_filters, name="hospital_admin_view_logs_choose_filters"),
    # 127.0.0.1/healthnet/hospital_admin_view_logs_choose_filters
]