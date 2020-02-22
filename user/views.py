import string
import random
import time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgetPasswordForm
from .models import Profile


def login(request):
    context = {}
    if request.method == 'GET':
        login_form = LoginForm()
    else:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def login_for_modal(request):
    login_form = LoginForm(request.POST)

    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data = {
            'status': 'SUCCESS',
        }
        return JsonResponse(data)
    else:
        data = {
            'status': 'ERROR',
        }
        return JsonResponse(data)


def register(request):
    context = {}
    if request.method == 'GET':
        reg_form = RegForm()
    else:
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            User.objects.create_user(username=username, email=email, password=password)
            # 清除session
            del request.session['register_code']
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def user_info(request):
    return render(request, 'user_info.html')


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {
        'form': form,
        'page_title': '修改昵称',
        'form_title': '修改昵称',
        'submit_text': '修改',
        'return_back_url': redirect_to,
    }
    return render(request, 'form.html', context)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {
        'form': form,
        'page_title': '绑定邮箱',
        'form_title': '绑定邮箱',
        'submit_text': '绑定',
        'return_back_url': redirect_to,
    }
    return render(request, 'bind_email.html', context)


def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.digits, 4))
        now = int(time.time())
        print(now)
        send_code_time = request.session.get('send_code_time', 0)
        print(send_code_time)
        print(now - send_code_time)
        if now - send_code_time < 30:
            data = {'status': 'ERROR'}
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now
            # 发送邮件
            send_mail(
                '绑定邮箱',
                '验证码：%s' % code,
                '578451004@qq.com',
                [email],
                fail_silently=False,
            )
            data = {'status': 'SUCCESS', }
    else:
        data = {'status': 'ERROR'}
    return JsonResponse(data)


def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {
        'form': form,
        'page_title': '修改密码',
        'form_title': '修改密码',
        'submit_text': '修改',
        'return_back_url': redirect_to,
    }
    return render(request, 'form.html', context)


def forget_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            print(email)
            user = User.objects.get(email=email)
            print(user)
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['forget_password_code']
            return redirect(redirect_to)
    else:
        form = ForgetPasswordForm()

    context = {
        'form': form,
        'page_title': '重置密码',
        'form_title': '重置密码',
        'submit_text': '确定',
        'return_back_url': redirect_to,
    }
    return render(request, 'forget_password.html', context)
