
from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from django.core.mail import send_mail
from django.conf import settings
import random


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'patient/patientsignup.html',context=mydict)

def patient_dashboard_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),

    }
   
    return render(request,'patient/patient_dashboard.html',context=dict)

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            patient= models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient=patient
            blood_request.save()
            return HttpResponseRedirect('my-request')  
    return render(request,'patient/makerequest.html',{'request_form':request_form})

def my_request_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request,'patient/my_request.html',{'blood_request':blood_request})


def ajaxemail(request):
    usercount=tbl_cus_reg.objects.filter(cus_email=request.GET.get("email")).count()
    marketcount=tbl_market_reg.objects.filter(mar_email=request.GET.get("email")).count()
    farmercount=tbl_farmer_reg.objects.filter(far_email=request.GET.get("email")).count()
    subadmincount=tbl_subadmin.objects.filter(sad_email=request.GET.get("email")).count()
    if usercount>0 or marketcount>0 or farmercount>0 or subadmincount>0:
        return render(request,"patient/Ajaxemail.html",{'mess':1})
    else:
         return render(request,"patient/Ajaxemail.html")


def CreateNewPass(request):
    if request.method=="POST":
        if request.POST.get('txtpassword2')==request.POST.get('txtpassword3'):
            usercount=tbl_cus_reg.objects.filter(cus_email=request.session["femail"]).count()
            marketcount=tbl_market_reg.objects.filter(mar_email=request.session["femail"]).count()
            farmercount=tbl_farmer_reg.objects.filter(far_email=request.session["femail"]).count()
            subadmincount=tbl_subadmin.objects.filter(sad_email=request.session["femail"]).count()
            if usercount>0:
                user=tbl_cus_reg.objects.get(cus_email=request.session["femail"])
                user.cus_pass=request.POST.get('txtpassword2')
                user.save()
                return redirect("webguest:login")

            elif marketcount>0:
                doc=tbl_market_reg.objects.get(mar_email=request.session["femail"])
                doc.marpassword=request.POST.get('txtpassword2')
                doc.save()
                return redirect("login")

            elif farmercount>0:
                con=tbl_farmer_reg.objects.get(far_email=request.session["femail"])
                con.far_pass=request.POST.get('txtpassword2')
                con.save()
                return redirect("login")

            else:
                hos=tbl_subadmin.objects.get(sad_email=request.session["femail"])
                hos.sad_pass=request.POST.get('txtpassword2')
                hos.save()
                return redirect("login")
    else:
        return render(request,"patient/CreateNewPassword.html")


def ForgetPassword(request):
    if request.method == "POST":
        otp = random.randint(10000, 999999)
        request.session["otp"] = otp
        request.session["femail"] = request.POST.get('txtemail')
        send_mail(
            'Respected Sir/Madam ',  # subject
            "\rYour OTP for Reset Password Is" + str(otp),  # body
            settings.EMAIL_HOST_USER,
            [request.POST.get('txtemail')],
        )
        return redirect("verification")
    else:
        return render(request, "patient/ForgetPassword.html")


def OtpVerification(request):
    if request.method == "POST":
        otp = int(request.session["otp"])
        if int(request.POST.get('txtotp')) == otp:
            return redirect("create")
    return render(request, "patient/OTPVerification.html")