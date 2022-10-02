from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.csrf import csrf_exempt
from ..models import user_list, ask_list
from app1.utils.encrypt import md5
from app1 import models
from django.http import HttpResponse
import json


class UserLogin(forms.ModelForm):
    class Meta:
        model = user_list
        fields = ["name", "password"]
        widgets = {
            "password": forms.PasswordInput
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


class UserRegister(forms.ModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput
    )
    class Meta:
        model = user_list
        fields = ["name", "gender", "email", "academy", "password", "confirm_password"]
        widgets = {
            "password": forms.PasswordInput
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm_password")
        confirm = md5(confirm)
        if confirm != pwd:
            raise ValidationError('密码不一致')
        return confirm

    def clean_password(self):
        # 让密码进来时就加密
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

def login(request):

    if request.method == 'GET':
        form = UserLogin()
        return render(request, 'login.html', {"form": form})
    
    form = UserLogin(data=request.POST)
    if form.is_valid():
        # print(form.cleaned_data)
        user_object = models.user_list.objects.filter(
            name=form.cleaned_data['name'], 
            password=form.cleaned_data['password']).first()
        if not user_object:
            # 如果匹配不到，输出错误信息，并返回当前页面
            form.add_error("password", "用户名或密码错误")
            return render(request, 'login.html', {"form": form})
        # print(user_object.id, user_object.name)
        # 添加cookie
        
        request.session["info"] = {'id': user_object.id, 'name': user_object.name}
        return redirect('/index')
        
    return render(request, 'login.html', {"form": form})



def register(request):
    if request.method == 'GET':
        form = UserRegister()
        return render(request, 'register.html', {"form": form})
    
    name_list = []
    name_objects = models.user_list.objects.all()
    for name_object in name_objects:
        name_list.append(name_object.name)
    print(name_list)

    form = UserRegister(data=request.POST)
    name = request.POST.get("name")
    if name in name_list:
        form.add_error("name", "此用户名已存在")
        return render(request, 'register.html', {"form": form})
    name_list.append(name)
    if form.is_valid():     #这里的原理不是很理解，is_valid会执行clean_confirm_password函数吗？如果执行的话，返回的也只会是confirm_password啊，只要输了应该就会为真吧
        # print(form.cleaned_data)
        form.save()
        return redirect('/login')
    return render(request, 'register.html', {"form": form})


def logout(request):

    info = request.session.get("info")
    if not info:
        return redirect('/login/')

    """注销"""
    request.session.clear()     #清除了浏览器里的cookie
    return redirect('/login/')


class Ask(forms.ModelForm):
    class Meta:
        model = ask_list
        fields = ["title", "ask_intro", "ask_kind"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

def ask(request, nid):

    info = request.session.get("info")
    if not info:
        return redirect('/login/')

    form = Ask()
    if request.method == 'GET':
        return render(request, 'ask_raise.html', {"form": form})

    
    asker_object = models.user_list.objects.filter(id=nid).first()
    form = Ask(data=request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.asker = asker_object
        obj.save()
    return redirect('/problem/set')



class UserHomepage(forms.ModelForm):
    class Meta:
        model = user_list
        fields = ["name", "gender", "academy", "email", "intro"]
        widgets = {
            "intro": forms.Textarea(attrs={'rows':1, 'cols':10}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}


def self_homepage(request, nid):

    info = request.session.get("info")
    if not info:
        return redirect('/login/')

    user_object = models.user_list.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = UserHomepage(instance=user_object)
        sort_kind = request.GET.get("s", "")
        problems_objects = []
        ans_objects = []
        agree_objects = []
        focus_objects = []
        if sort_kind == "ask":
            problems_objects = models.ask_list.objects.filter(asker=user_object).all()
        elif sort_kind == "ans":
            ans_objects = models.ans_list.objects.filter(author=user_object).all()
        elif sort_kind =="agree":
            agree_objects = user_object.vote_ans.all()
        elif sort_kind == "focus":
            focus_objects = user_object.focus_ask.all()
        self_dict = {
            "id": nid,
            "user": user_object,
            "problems": problems_objects,
            "answers": ans_objects,
            "agrees": agree_objects,
            "focuses": focus_objects,
            "form": form
        }
        return render(request, 'self_homepage.html', self_dict)

    form = UserHomepage(instance=user_object, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/"+str(nid)+"/homepage")




@csrf_exempt
def ask_delete(request):
    problem_id = request.POST.get("problem_id")
    models.ask_list.objects.filter(id=problem_id).delete()
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def ans_delete(request):
    answer_id = request.POST.get("answer_id")
    models.ans_list.objects.filter(id=answer_id).delete()
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def agree_delete(request):
    answer_id = request.POST.get("agree_id")
    answer_object = models.ans_list.objects.filter(id=answer_id).first()
    user_id = request.session["info"]["id"]
    user_object = models.user_list.objects.filter(id=user_id).first()
    user_object.vote_ans.remove(answer_object)
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def focus_delete(request):
    problem_id = request.POST.get("focus_id")
    problem_object = models.ask_list.objects.filter(id=problem_id).first()
    user_id = request.session["info"]["id"]
    user_object = models.user_list.objects.filter(id=user_id).first()
    user_object.focus_ask.remove(problem_object)
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def ask_edit(request):
    problem_id = request.POST.get("problem_id")
    print(problem_id)
    problem_object = models.ask_list.objects.filter(id=problem_id).first()

    data_dict = {'status': True, 'problem_title': problem_object.title}
    return HttpResponse(json.dumps(data_dict))
    

@csrf_exempt
def ask_edit_confirm(request):
    problem_id = request.POST.get("edit_id")
    problem_content = request.POST.get("problem_content")
    problem_object = models.ask_list.objects.get(id=problem_id)
    problem_object.title = problem_content
    problem_object.save()
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def ans_edit(request):
    answer_id = request.POST.get("answer_id")
    answer_object = models.ans_list.objects.filter(id=answer_id).first()

    data_dict = {'status': True, 'answer_content': answer_object.ans_content}
    return HttpResponse(json.dumps(data_dict))


@csrf_exempt
def ans_edit_confirm(request):
    answer_id = request.POST.get("edit_id")
    answer_content = request.POST.get("answer_content")
    answer_object = models.ans_list.objects.get(id=answer_id)
    answer_object.ans_content = answer_content
    answer_object.save()
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))