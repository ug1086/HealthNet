from django import forms
from django.contrib.auth.models import User
from healthnet.models import UserProfile,Patient

class UserForm(forms.ModelForm):
    '''Form for User model
    Author:Smruthi
    date: 30 Sep 2016'''
    password=forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    '''Form for UserProfile model
        Author:Smruthi
        date: 30 Sep 2016'''
    class Meta:
        model = Patient
        # fields=('first_name','last_name','contactnumber','emergencycontact',)
        fields=('first_name','last_name','age','height','weight','insurance_company','insurance_id','hospital','address','contact_number','emergency_contact_number')
