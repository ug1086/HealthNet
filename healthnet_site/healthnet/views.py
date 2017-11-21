from django.http import HttpResponseRedirect
from healthnet.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login,logout
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from .models import *
from django.db.models import Q
from .functions import determine_action


def index(request):
    """
    Displays the landing page if the user not active
    Re-routes to the appointments page for the user if they are active.

    Author: Nick Deyette
    """
    if request.user.is_authenticated():
        if request.user.userprofile.user_type == "admin":
            return redirect('/healthnet/hospital_admin_index')
        else:
            return redirect('/healthnet/appointments')
    if request.method == "POST":
        button_choice = request.POST.get('button_choice')

        if button_choice == "Login":
            return redirect('/healthnet/Login')
        else:
            return redirect('/healthnet/register')
    return render(request, 'healthnet/index.html')


def appointments(request):
    """
    Displays all appointments that can be viewed/edited by current user
    Patient or Doctor: Can view their own appointments
    Nurse: Can view all appointments for the current week

    Author: Kyler Freas
    """

    if not request.user.is_authenticated():
        return redirect('/healthnet/Login')

    user_id = request.user.id
    username = User.objects.get(pk=user_id).username
    user_type = request.user.userprofile.user_type

    appt_list = Appointment.objects.order_by('-start').reverse()

    if user_type == 'patient':
        patient_id = Patient.objects.get(user_id=user_id).id
        appt_list = [appt for appt in appt_list if appt.patient_id == patient_id]

    if user_type == 'doctor':
        doctor_id = Doctor.objects.get(user_id=user_id).id
        appt_list = [appt for appt in appt_list if appt.doctor_id == doctor_id]

    if user_type == 'nurse':
        date = datetime.datetime.today().replace(tzinfo=None)
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(7)

        appt_list = [appt for appt in appt_list if start_week <= appt.start.replace(tzinfo=None) <= end_week]

    if request.POST.get('create an appointment'):
        return redirect('/healthnet/create_appointment')

    if request.POST.get('edit_info'):
        return redirect('/healthnet/edit_profile_information/%s' % user_id)

    if request.POST.get('logout'):
        logout(request)
        Logger.log_system_activity(activity="has logged out", username1=username)
        return HttpResponseRedirect('index.html')

    data = []
    for appt in appt_list:
        # Calendar title for the appointment
        appt_title = User.objects.get(id=Doctor.objects.get(id=appt.doctor_id).user_id)

        # Show patient if current user is a doctor. Otherwise, show doctor.
        if user_type == 'doctor':
            appt_title = User.objects.get(id=Patient.objects.get(id=appt.patient_id).user_id)

        data.append(
            {
                'id': appt.id,
                'title': appt_title,
                'start': appt.start.replace(tzinfo=None, microsecond=0).isoformat(),
                'end': appt.end.replace(tzinfo=None, microsecond=0).isoformat()
            })

    context = {'appt_list': appt_list, 'json_data': data, 'username': username, 'user_type': user_type}
    return render(request, 'healthnet/appointments.html', context)

def create_appointment(request):
    """
    Allows user to save a new appointment
    This action is logged

    Author: Kyler Freas
    """
    user_id = request.user.id
    username = request.user.username
    user_type = request.user.userprofile.user_type

    doc_list = Doctor.objects.all()
    patient_list = Patient.objects.all()

    if request.POST.get('create'):
        if user_type == 'doctor':
            doctor_id = Doctor.objects.get(user_id=user_id).id
            doctor_username = User.objects.get(pk=user_id).username
        else:
            doctor_id = request.POST.get('doctor')
            doctor_user_id = Doctor.objects.get(pk=doctor_id).user_id
            doctor_username = User.objects.get(pk=doctor_user_id).username

        if user_type == 'patient':
            patient_id = Patient.objects.get(user_id=user_id).id
            patient_username = User.objects.get(pk=user_id).username
        else:
            patient_id = request.POST.get('patient')
            patient_user_id = Patient.objects.get(pk=patient_id).user_id
            patient_username = User.objects.get(pk=patient_user_id).username

        appt_start = request.POST.get('start')
        appt_end = request.POST.get('end')
        appt_location = Patient.objects.get(id=patient_id).hospital

        # Check for time conflicts
        doc_conflict = Appointment.objects.filter(doctor_id=doctor_id, start__gte=appt_start, start__lte=appt_end).exists() or Appointment.objects.filter(doctor_id=doctor_id, end__gte=appt_start, end__lte=appt_end).exists()
        patient_conflict = Appointment.objects.filter(patient_id=patient_id, start__gte=appt_start, end__lte=appt_end).exists()

        # If there is a time conflict, abort saving the appointment
        if doc_conflict:
            context = {'doc_list': doc_list, 'patient_list': patient_list, 'username': username, 'doc_conflict': doc_conflict}
            return render(request, 'healthnet/create_appointment.html', context)
        elif patient_conflict:
            context = {'doc_list': doc_list, 'patient_list': patient_list, 'username': username, 'patient_conflict': patient_conflict}
            return render(request, 'healthnet/create_appointment.html', context)

        new_appointment = Appointment(doctor_id=doctor_id, patient_id=patient_id, location=appt_location, start=appt_start, end=appt_end)
        new_appointment.save()

        Logger.log_system_activity(activity="has created an appointment with", username1=doctor_username, username2=patient_username)

        return redirect('/healthnet/appointments/')

    if request.POST.get("back"):
        return redirect('/healthnet/appointments')

    context = {'doc_list': doc_list, 'patient_list': patient_list, 'username': username}
    return render(request, 'healthnet/create_appointment.html', context)

def view_appointment(request, appointment_id):
    """
    Displays data for an appointment
    :param appointment_id: id of appointment to be viewed in the database

    Author: Kyler Freas
    """
    username = request.user.username
    user_type = request.user.userprofile.user_type

    if request.POST.get('delete'):
        return redirect('/healthnet/delete_appointment/%s' % appointment_id)
    if request.POST.get("back"):
        return redirect('/healthnet/appointments')
    if request.POST.get("edit"):
        return redirect('/healthnet/update_appointment/%s' % appointment_id)
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        # No appointment with the given id found
        raise Http404("Appointment does not exist")

    doctor = Doctor.objects.get(id=appointment.doctor_id)
    patient = Patient.objects.get(id=appointment.patient_id)
    appt_start = appointment.start
    appt_end = appointment.end

    return render(request, 'healthnet/view_appointment.html', {'doctor': doctor, 'patient': patient, 'start': appt_start, 'end': appt_end, 'id': appointment_id, 'username': username, 'user_type': user_type})


def update_appointment(request, appointment_id):
    """
    Allows user to update an existing appointment
    :param appointment_id: id of appointment to be saved in the database

    This action is logged.

    Author: Kyler Freas
    """
    username = request.user.username
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        # No appointment with the given id found
        raise Http404("Appointment does not exist")

    user_id = request.user.id
    user_type = request.user.userprofile.user_type

    doc_list = Doctor.objects.all()
    patient_list = Patient.objects.all()

    str_start = appointment.start.replace(tzinfo=None, microsecond=0).isoformat()
    str_end = appointment.end.replace(tzinfo=None, microsecond=0).isoformat()

    if request.POST.get('delete'):
        return redirect('/healthnet/delete_appointment/%s' % appointment_id)
    elif request.POST.get('cancel'):
        return redirect('/healthnet/view_appointment/%s' % appointment_id)
    elif request.POST.get('update'):
        if user_type == 'doctor':
            new_doc = Doctor.objects.get(user_id=user_id).id
            doctor_username = User.objects.get(pk=user_id).username
        else:
            new_doc = request.POST.get('doctor')
            new_doc_user_id = Doctor.objects.get(pk=new_doc).user_id
            doctor_username = User.objects.get(pk=new_doc_user_id)

        if user_type == 'patient':
            new_patient = Patient.objects.get(user_id=user_id).id
            patient_username = User.objects.get(pk=user_id).username
        else:
            new_patient = request.POST.get('patient')
            new_patient_user_id = Patient.objects.get(pk=new_patient).user_id
            patient_username = User.objects.get(pk=new_patient_user_id)

        new_start = request.POST.get('start')
        new_end = request.POST.get('end')

        if new_start != str_start and new_end != str_end:
            doctor = Doctor.objects.get(id=appointment.doctor_id)
            patient = Patient.objects.get(id=appointment.patient_id)

            # Check for time conflicts
            doc_conflict = Appointment.objects.filter(doctor_id=appointment.doctor_id, start=new_start).exists()
            patient_conflict = Appointment.objects.filter(patient_id=appointment.patient_id, start=new_start).exists()

            # If there is a time conflict, abort saving the appointment
            if doc_conflict:
                context = {'doc_list': doc_list, 'patient_list': patient_list, 'doctor': doctor, 'patient': patient, 'start': new_start, 'end': new_end, 'id': appointment_id, "user_type": user_type, 'username': username, 'doc_conflict': doc_conflict}
                return render(request, 'healthnet/update_appointment.html', context)
            elif patient_conflict:
                context = {'doc_list': doc_list, 'patient_list': patient_list, 'doctor': doctor, 'patient': patient, 'start': new_start, 'end': new_end, 'id': appointment_id, "user_type": user_type, 'username': username, 'patient_conflict': patient_conflict}
                return render(request, 'healthnet/update_appointment.html', context)

        appointment.update_appointment(new_doc, new_patient, new_start, new_end)

        Logger.log_system_activity(activity="has updated an appointment with", username1=doctor_username, username2=patient_username)

        return redirect('/healthnet/appointments/')

    doctor = Doctor.objects.get(id=appointment.doctor_id)
    patient = Patient.objects.get(id=appointment.patient_id)
    # Convert date to ISO in order to show in form's date picker
    str_datetime = appointment.start.replace(tzinfo=None, microsecond=0).isoformat()

    return render(request, 'healthnet/update_appointment.html',
            {'doc_list': doc_list, 'patient_list': patient_list, 'doctor': doctor, 'patient': patient, 'start': str_start, 'end': str_end, 'id': appointment_id, "user_type": user_type, 'username': username})

def delete_appointment(request, appointment_id):
    """
    Displays the confirmation page for deleting an appointment.
    This action is logged.

    :param: appointment_id: id of appointment that is being displayed

    Author: Nick Deyette
    """
    username = request.user.username
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        raise Http404("Appointment does not exist")

    if request.POST.get('confirm'):
        appointment.delete()
        doctor_user_id = Doctor.objects.get(pk=appointment.doctor_id).user_id
        doctor_username = User.objects.get(pk=doctor_user_id)
        patient_user_id = Patient.objects.get(pk=appointment.patient_id).user_id
        patient_username = User.objects.get(pk=patient_user_id)
        Logger.log_system_activity(activity="has deleted an appointment with", username1=doctor_username, username2=patient_username)
        return redirect('/healthnet/appointments/')
    elif request.POST.get('deny'):
        return redirect('/healthnet/view_appointment/%s' % appointment_id)

    doctor = Doctor.objects.get(id=appointment.doctor_id)
    patient = Patient.objects.get(id=appointment.patient_id)
    datetime = appointment.start

    return render(request, 'healthnet/delete_appointment.html', {'doctor': doctor, 'patient': patient, 'datetime': datetime, 'username': username})

def hospital_admin_index(request):
    """
    Displays the index for hospital admins.

    Author: Nick Deyette
    """
    user_name = request.user.username
    if request.method == "POST":
        if request.POST.get('create'):
            return redirect('/healthnet/hospital_admin/create_user')
        elif request.POST.get('view_logs'):
            return redirect('/healthnet/hospital_admin/view_logs')
        else:
            username = request.user.username
            logout(request)
            Logger.log_system_activity(activity="has logged out", username1=username)
            return redirect('/healthnet/Login.html')
    return render(request, 'healthnet/hospital_admin_index.html', {'username': user_name})

def hospital_admin_create_user(request):
    """
    Displays the page that allows a hospital admin to create a new user (Doctor, Nurse, Admin)
    This action is logged

    Author: Nick Deyette
    """
    user_name = request.user.username
    admin_username = User.objects.get(pk=request.user.id).username
    if request.method == "POST":
        if request.POST.get("submit"):
            user_type = request.POST.get("user_type")
            username = request.POST.get("username")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            hospital = Hospital.objects.get(pk=request.POST.get("hospital"))
            password = request.POST.get("password")
            new_user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            new_user.save()
            Logger.log_system_activity(activity="has created a new user:", username1=admin_username, username2=username)
            if user_type == "nurse":
                new_nurse = Nurse(user_id=new_user.pk, hospital=hospital)
                new_nurse.save()
                user_profile = UserProfile(user=new_user, user_type="nurse")
                user_profile.save()
            elif user_type == "doctor":
                new_doctor = Doctor(user_id=new_user.pk, hospital=hospital)
                new_doctor.save()
                user_profile = UserProfile(user=new_user, user_type="doctor")
                user_profile.save()
            else:
                new_admin = Administrator(user_id=new_user.pk, hospital=hospital)
                new_admin.save()
                user_profile = UserProfile(user=new_user, user_type="admin")
                user_profile.save()
            return redirect('/healthnet/hospital_admin_create_user_success')
        else:
            return redirect('/healthnet/hospital_admin_index')

    hospital_list = Hospital.objects.all()
    return render(request, 'healthnet/hospital_admin_create_user.html', {'username': user_name, 'hospital_list': hospital_list})

def hospital_admin_create_user_success(request):
    """
    Displays a page stating that the creation of the user was
    successful

    Author: Nick Deyette
    """
    username = request.user.username
    if request.method == "POST":
        return redirect('/healthnet/hospital_admin_index')
    return render(request, 'healthnet/hospital_admin_create_user_success.html', {'username': username})

def hospital_admin_create_user_failure(request):
    """
    Displays a page stating that the creation of the user was
    a failure.

    Author: Nick Deyette
    """
    username = request.user.username
    if request.POST.get('back'):
        return redirect('/healthnet/hospital_admin/create_user')
    return render(request, 'healthnet/hospital_admin_create_user_failure.html', {'username': username})


def hospital_admin_view_logs(request):
    """
    Displays all of the log actions

     Author: Nick Deyette
    """
    username = request.user.username
    filter = "None"

    if request.POST.get("back"):
        return redirect('/healthnet/hospital_admin_index')
    if request.POST.get("filter"):
        return redirect('/healthnet/hospital_admin_view_logs_create_filters')
    logs = LogItem.objects.order_by('-timestamp')

    context = {'logs': logs, 'username': username, 'filter': filter}

    return render(request, 'healthnet/hospital_admin_view_logs.html', context)

def hospital_admin_view_logs_with_filters(request, start_date, end_date, user_name, user_type, action):
    username = request.user.username
    user_type = user_type.lower()
    action_message = determine_action(action)

    if request.POST.get("back"):
        return redirect('/healthnet/hospital_admin_index')

    if start_date != '' and end_date != '' and user_name != '' and user_type != '' and action != '':
        # filter by date, username, user type and action
        filter = start_date + " to " + end_date + " for " + user_name + " of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type != '' and action == '':
        # filter by date, username and user type
        filter = start_date + " to " + end_date + " for " + user_name + " of type: " + user_type
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type))).order_by("-timestamp")
    elif start_date != '' and end_date != '' and user_name != '' and user_type == '' and action != '':
        # filter by date, username and action
        filter = start_date + " to " + end_date + " for " + user_name + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type != '' and action != '':
        # filter by date, user type and action
        filter = start_date + " to " + end_date + " of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type != '' and action != '':
        # filter by username, user type and action
        filter = " For " + user_name + " of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type == '' and action == '':
        # filter by date and username
        filter = start_date + " to " + end_date + " for " + user_name
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type != '' and action == '':
        # filter by date and user type
        filter = start_date + " to " + end_date + " of type: " + user_type
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(user_type1=user_type) | Q(user_type2=user_type))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type != '' and action == '':
        # filter by username and user type
        filter = "For " + user_name + " of type: " + user_type
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type == '' and action != '':
        # filter by date and action
        filter = start_date + " to " + end_date + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type == '' and action != '':
        # filter by username and action
        filter = " For " + user_name + " of action: " + action
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type != '' and action != '':
        # filter by user type and action
        filter = " Of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter((Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type != '' and action == '':
        # filter by user type
        filter = "Of type: " + user_type
        filtered_logs = LogItem.objects.filter(Q(user_type1=user_type) | Q(user_type2=user_type)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type == '' and action == '':
        # filter by username
        filter = "For " + user_name
        filtered_logs = LogItem.objects.filter(Q(username1=user_name) | Q(username2=user_name)).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type == '' and action == '':
        # filter by date
        filter = start_date + " to " + end_date
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date])).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type == '' and action != '':
        # filter by action
        filter = " Of action: " + action
        filtered_logs = LogItem.objects.filter(Q(activity__icontains=action_message)).order_by('-timestamp')
    else:
        # no filters
        return hospital_admin_view_logs(request)

    return render(request, 'healthnet/hospital_admin_view_logs.html', {'logs': filtered_logs, 'username': username, 'filter': filter})

def hospital_admin_view_logs_create_filters(request):
    """
    Displays the page responsible for allowing an admin to create filters
    for log activities.

    Author: Nick Deyette
    """
    username = request.user.username

    if request.POST.get('back_create'):
        return redirect('/healthnet/hospital_admin/view_logs')

    if request.POST.get('back_choose'):
        return redirect('/healthnet/hospital_admin_view_logs_create_filters')

    if request.POST.get('submit_create'):
        if request.POST.get('date'):
            date = request.POST.get('date')
        else:
            date = ''
        if request.POST.get('username'):
            user_name = request.POST.get('username')
        else:
            user_name = ''
        if request.POST.get('user_type'):
            user_type = request.POST.get('user_type')
        else:
            user_type = ''
        if request.POST.get('action'):
            action = request.POST.get('action')
        else:
            action = ''

        user_list = User.objects.all
        user_type_list = ['Patient', 'Nurse', 'Doctor', 'Admin']
        action_list = ['Logging In', 'Logging Out', 'Create Appointment', 'Update Appointment', 'Delete Appointment', 'Create User', 'Update Profile Info', 'Register', 'Change Password']
        return render(request, 'healthnet/hospital_admin_view_logs_choose_filters.html', {'username': username, 'date': date, 'user_name': user_name, 'user_type': user_type, 'user_list': user_list, 'user_type_list': user_type_list, 'action': action, 'action_list': action_list})

    if request.POST.get('submit_choose'):
        if request.POST.get('start_date'):
            start_date = request.POST.get('start_date')
        else:
            start_date = ''
        if request.POST.get('end_date'):
            end_date = request.POST.get('end_date')
        else:
            end_date = ''
        if request.POST.get('user_name'):
            user_name = request.POST.get('user_name')
        else:
            user_name = ''
        if request.POST.get('user_type'):
            user_type = request.POST.get('user_type')
        else:
            user_type = ''
        if request.POST.get('action'):
            action = request.POST.get('action')
        else:
            action = ''
        return hospital_admin_view_logs_with_filters(request, start_date, end_date, user_name, user_type, action)

    return render(request, 'healthnet/hospital_admin_view_logs_create_filters.html', {'username': username})

def edit_profile_information(request, user_id):
    """
    Displays the page allowing a Patient to edit their information
    This action is logged

    :param user_id: the user_id of the patient editing their page
    """
    user = User.objects.get(pk=user_id)
    username = User.objects.get(pk=user_id).username
    patient = Patient.objects.get(user_id=user_id)
    contact_number = patient.contact_number
    emergency_contact_number = patient.emergency_contact_number
    first_name = patient.first_name
    last_name = patient.last_name

    if request.POST.get('submit'):
        new_contact_number = request.POST.get('contact_number')
        if new_contact_number == "" or len(new_contact_number) < 10:
            return redirect('/healthnet/edit_profile_information_failure')
        new_emergency_contact_number = request.POST.get('emergency_contact_number')
        if new_emergency_contact_number == "" or len(new_emergency_contact_number) < 10:
            return redirect('/healthnet/edit_profile_information_failure')
        patient.update_profile_info(new_contact_number=new_contact_number, new_emergency_contact_number=new_emergency_contact_number)
        Logger.log_system_activity(activity="has updated their profile information", username1=user.username, user_type1="patient")
        return redirect('/healthnet/appointments')
    elif request.POST.get('cancel'):
        return redirect('/healthnet/appointments')
    elif request.POST.get('password'):
        return redirect('/healthnet/change_password/%s' % user_id)

    context = {'user': user, 'contact_number': contact_number, 'emergency_contact_number': emergency_contact_number, 'username': username, 'first_name': first_name, 'last_name': last_name}

    return render(request, 'healthnet/edit_profile_information.html', context)

def edit_profile_information_failure(request):
    """
    Displays a page when an error occurs in editing profile
    information.

    Author: Nick Deyette
    """
    if request.POST.get('back'):
        return redirect('/healthnet/edit_profile_information/%s' % request.user.id)
    return render(request, 'healthnet/edit_profile_information_failure.html', {'username': request.user.username})

def register_success(request):
    '''to display the successful registration message
    Author:Smruthi
    date: 30 Sep 2016'''
    return render(request,'healthnet/Success.html')

def register(request):
    '''view to register new user
    fetches the data from the form and saves the information required for registering the new Patient
    Author:Smruthi
    date: 30 Sep 2016
    this action is logged'''
    context=RequestContext(request)
    registered=False
    if request.method == 'POST':
        if request.POST.get('submit'):
            new_user_form=UserForm(data=request.POST)
            new_profile_form=UserProfileForm(data=request.POST)


            if new_user_form.is_valid() and new_profile_form.is_valid():
                user=new_user_form.save()
                user.set_password(user.password)
                user.save()

                user_id = user.pk

                profile=new_profile_form.save(commit=False)

                user_profile = UserProfile(user=user, user_type="patient")

                user_profile.save()
                patient_obj=Patient(
                    user_id=user_id,
                    first_name=profile.first_name,
                    last_name=profile.last_name,
                    age=profile.age,
                    weight=profile.weight,
                    height=profile.height,
                    insurance_company=profile.insurance_company,
                    insurance_id=profile.insurance_id,
                    hospital=profile.hospital,
                    address=profile.address,
                    contact_number=profile.contact_number,
                    emergency_contact_number=profile.emergency_contact_number)
                patient_obj.save()
                Logger.log_system_activity(activity="has registered", username1=user.username)
                registered=True
                return redirect('/healthnet/index')
            else:
                print (new_user_form.errors,new_profile_form.errors)
        elif request.POST.get('back'):
            return redirect('/healthnet/index')
        else:
            return redirect('/healthnet/index')
    else:
        new_user_form=UserForm()
        new_profile_form=UserProfileForm()
    return render_to_response('healthnet/Registration.html',{'user_form':new_user_form,'profile_form':new_profile_form,'registered':registered},context)



def user_login(request):
    '''Vew to login  user and route to home page
    Author:Smruthi
    date: 30 Sep 2016
    this action is logged'''
    if request.POST.get('submit'):
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request, user)
                Logger.log_system_activity(activity="has logged in", username1=username)

                user_id = request.user.id
                user = User.objects.get(pk=user_id)
                user_type = UserProfile.objects.get(user=user).user_type
                if user_type == "admin":
                    return HttpResponseRedirect('hospital_admin_index')
                return HttpResponseRedirect('appointments')
            else:
                return HttpResponse('Your account is inactive')
        else:
            return redirect('/healthnet/login/invalid_login')
    elif request.POST.get('back'):
        return redirect('/healthnet/index/')
    else:
        return render(request,'healthnet/Login.html')



def user_logout(request):
    '''View to logout and route to index page
    Author:Smruthi
    date: 30 Sep 2016
    this action is logged'''
    username = request.user.username
    logout(request)
    Logger.log_system_activity(activity="has logged out", username1=username)
    return HttpResponseRedirect('index.html')

def invalid_login(request):
    """
    Displays the page for an invalid login

    Author: Nick Deyette
    """
    if request.method == "POST":
        return redirect('/healthnet/Login')
    return render(request, 'healthnet/invalid_login.html')

def change_password(request, user_id):
    """
    Displays the page for changing a Patient's password.

    Authenticates that the password and username are correct.
    :param user_id: user id of the Patient attempting to change their password

    Author: Nick Deyette
    """
    username = User.objects.get(pk=user_id)
    if request.POST.get('submit'):
        old_password = request.POST.get('old_pw')
        new_password = request.POST.get('new_pw')
        new_password_confirm = request.POST.get('new_pw_2')

        user = authenticate(username=username, password=old_password)

        if user:
            if new_password == new_password_confirm:
                user.set_password(new_password)
                user.save()
                Logger.log_system_activity(activity="has changed their password", username1=username)
            else:
                return redirect('/healthnet/invalid_password_change_1')
        else:
            return redirect('/healthnet/invalid_password_change_2')
        return redirect('/healthnet/edit_profile_information/%s' % user_id)
    elif request.POST.get('back'):
        return redirect('/healthnet/edit_profile_information/%s' % user_id)

    return render(request, 'healthnet/change_password.html', {'username': username})

def invalid_password_change_1(request):
    """
    Displays the page for changing a password and the two new passwords
    do not match.

    Author: Nick Deyette
    """
    if request.POST.get('back'):
        user_id = request.user.id
        return redirect('/healthnet/change_password/%s' % user_id)
    return render(request, 'healthnet/invalid_password_change_1.html')

def invalid_password_change_2(request):
    """
    Displays the page for changing a password and the password
    is not correct.

    Author: Nick Deyette
    """
    if request.POST.get('back'):
        user_id = request.user.id
        return redirect('/healthnet/change_password/%s' % user_id)
    return render(request, 'healthnet/invalid_password_change_2.html')