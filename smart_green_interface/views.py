from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from smart_green_interface.models import SiteContact, SiteWorkingHoursDetail
from datetime import datetime


# Create your views here.


def login_view(request):
    return render(request, 'login_temp.html')


def authentication_test(user_email, user_password):
    user = authenticate(username=user_email, password=user_password)
    if user is not None:
        # the password verified for the user
        if user.is_active:
            return True
        else:
            return False
    else:
        # the authentication system was unable to verify the username and password
        return False


def verify_pass(request):
    if 'user_email' in request.POST and 'user_pass' in request.POST:
        user_password = request.POST['user_pass']
        user_email = request.POST['user_email']
        if not SiteContact.objects.filter(email=user_email, password=user_password).exists():
            return render(request, 'login_temp.html', {'message': 'Please Check Up Your Email And Password'
                                                       ,'type': 'alert alert-danger'
                                                       , 'bolded_message': 'ERROR: '})
        else:
            user_list = SiteContact.objects.filter(email=user_email)
            if user_list[0].password == '1234567890':  # default password
                return HttpResponseRedirect(redirect_to='/change_pass/')
            else:
                request.session['user_email'] = user_email
                return HttpResponseRedirect(redirect_to='/dashboard/')


def change_pass(request):
    return render(request, 'change_password.html', {'message': 'Please Change Your Default Password'
        , 'type': 'alert alert-info'
        , 'bolded_message': 'INFO: '})


def confirm_change_pass(request):
    if not 'user_email' in request.POST and 'user_pass' in request.POST and 'user_pass_verify' in request.POST:
        return render(request, 'change_password.html', {'message': 'Something Go Wrong, Please Do It Again'
                                                        , 'type': 'alert alert-danger'
                                                        , 'bolded_message': 'ERROR: '})
    else:
        user_pass = request.POST['user_pass']
        user_pass_verify = request.POST['user_pass_verify']
        user_email = request.POST['user_email']
        if is_password_valid(user_pass, user_pass_verify):
            change_password_for_contact(user_email, user_pass)
            request.session['user_email'] = user_email
            return HttpResponseRedirect(redirect_to='/dashboard/')
        else:
            return render(request, 'change_password.html',
                          {'message': 'Invalid Password, password length should be longer then 7'})


def is_password_valid(pass1, pass2):
    # add length check
    return pass1 == pass2 and pass1 != '1234567890' and len(pass1) > 7


def change_password_for_contact(email, password):
    site_contants = SiteContact.objects.filter(email=email, password='1234567890')
    for site_contant in site_contants:
        site_contant.password = password
        site_contant.save()


def dashboard(request):
    user_site_list = SiteContact.objects.filter(email=request.session['user_email'])
    data_list = []
    for user_site in user_site_list:
        data_list.append(SiteWorkingHoursDetail.objects.filter(site_id=user_site.site_id))
    return render(request, 'dashboard.html', {'data': data_list})


def theme(request):
    return render(request, 'bootstrap_theme.html')


def sort_open_hours_by_date(request):
    start_date, end_date = date_set_up(request)
    user_site_list = SiteContact.objects.filter(email=request.session['user_email'])
    data_list = []
    for user_site in user_site_list:
        data_list.append(
            SiteWorkingHoursDetail.objects.filter(site_id=user_site.site_id, date__range=[start_date, end_date]))
    return render(request, 'dashboard.html', {'data': data_list})


def date_validation(start_date, end_date):
    if start_date > end_date:
        return end_date, start_date
    else:
        return  start_date, end_date


def date_set_up(request):
    if not 'start_date' in request.POST or request.POST['start_date'] == '':
        start_date = str(datetime.now())
        start_date = start_date.split(' ')[0]
    else:
        start_date = request.POST['start_date']
    if not 'end_date' in request.POST or request.POST['end_date'] == '':
        end_date = str(datetime.now())
        end_date = end_date.split(' ')[0]
    else:
        end_date = request.POST['end_date']
    return date_validation(start_date, end_date)
