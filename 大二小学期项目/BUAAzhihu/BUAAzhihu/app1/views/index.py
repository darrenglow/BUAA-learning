from re import search
from urllib.request import HTTPRedirectHandler
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django import forms
from app1 import models
from django.views.decorators.csrf import csrf_exempt
import json
from app1.utils.pagination import Pagination

def show_homepage(request):

    # 检查用户是否已经登录
    info = request.session.get("info")
    if not info:
        return redirect('/login/')


    user_id = request.session['info']['id']
    user_object = models.user_list.objects.filter(id=user_id).first()
    agree_list = []
    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["ans_content__contains"] = search_data

    sort_kind = request.GET.get("sort", "")
    if sort_kind == "rec" or not sort_kind:
        answers = models.ans_list.objects.filter(**data_dict).order_by("?")
    elif sort_kind == "time":
        answers = models.ans_list.objects.filter(**data_dict).order_by("-ans_time")
    elif sort_kind == "hot":
        answers = models.ans_list.objects.filter(**data_dict).order_by("-see_num")
    
    tag_kind = request.GET.get("tag", "")
    if tag_kind == "xuexi":
        answers = models.ans_list.objects.filter(thisask__ask_kind=1).all()
    elif tag_kind == "shenghuo":
        answers = models.ans_list.objects.filter(thisask__ask_kind=2).all()
    elif tag_kind == "tucao":
        answers = models.ans_list.objects.filter(thisask__ask_kind=3).all()
    elif tag_kind == "xuanke":
        answers = models.ans_list.objects.filter(thisask__ask_kind=4).all()



    agree_answers = user_object.vote_ans.all()
    for answer in answers:
        if answer in agree_answers:
            agree_list.append(1)
        else:
            agree_list.append(0)

    # 列表存储每个回答的赞同数
    vote_ans_list = []
    for answer in answers:
        num = answer.user_list_set.all().count()
        vote_ans_list.append(num)

    page_object = Pagination(request, answers, page_size=10)
    return render(request, 'homepage.html', {"user_id": info['id'], "answers": page_object.page_queryset, 
                                            "search_data": search_data, "agree_list": agree_list,
                                            'page_string': page_object.html(), "vote_ans_list": vote_ans_list})


def problem_set(request):
    info = request.session.get("info")
    if not info:
        return redirect('/login/')


    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["title__contains"] = search_data

    problem_list = models.ask_list.objects.filter(**data_dict).order_by("-ask_time")

    tag_kind = request.GET.get("tag", "")
    if tag_kind == "xuexi":
        problem_list = models.ask_list.objects.filter(ask_kind=1).all()
    elif tag_kind == "shenghuo":
        problem_list = models.ask_list.objects.filter(ask_kind=2).all()
    elif tag_kind == "tucao":
        problem_list = models.ask_list.objects.filter(ask_kind=3).all()
    elif tag_kind == "xuanke":
        problem_list = models.ask_list.objects.filter(ask_kind=4).all()

    page_object = Pagination(request, problem_list, page_size=10)
    return render(request, 'problem_set.html', {"problems": page_object.page_queryset, "user_id": request.session['info']['id'], 
                                                "search_data": search_data, "page_string":page_object.html()})
    
def problem_page(request, nid):
    info = request.session.get("info")
    if not info:
        return redirect('/login/')


    problem_object = models.ask_list.objects.filter(id=nid).first()
    answers_object = models.ans_list.objects.filter(thisask=nid).all()
    answers_num = answers_object.count()
    followers = problem_object.user_list_set.all().count()
    author_id = request.session['info']['id']
    author_object = models.user_list.objects.filter(id=author_id).first()
    problems_focus = author_object.focus_ask.all()
    if problem_object in problems_focus:
        status = True;
    else: 
        status = False;
    problem_dict = {"problem": problem_object, 
                    "answers": answers_object, 
                    "followers": followers,
                    "answers_num": answers_num,
                    "focus_status": status,
                    }

    if request.method == 'GET':
        return render(request, 'problem_page.html', problem_dict)

    ans = request.POST.get("answer_sheet")
    
    have_answered = models.ans_list.objects.filter(author_id=author_id, thisask_id=nid).first() #每个用户对于一个问题只能答一次
    if not have_answered:
        models.ans_list.objects.create(ans_content=ans, author=author_object, thisask=problem_object)
    answers_object = models.ans_list.objects.filter(thisask=nid).all()
    answers_num = answers_object.count()
    problem_dict["answers_num"] = answers_num
    return render(request, 'problem_page.html',problem_dict)


def answer_page(request, pid, nid):

    info = request.session.get("info")
    if not info:
        return redirect('/login/')


    comment = request.POST.get("pinglun")
    commenter_id = request.session['info']['id']
    commenter = models.user_list.objects.filter(id=commenter_id).first()
    thisanswer = models.ans_list.objects.filter(id=nid).first()
    


    if request.method == 'GET':
        problem_object = models.ask_list.objects.filter(id=pid).first()
        vote_num = thisanswer.user_list_set.all().count()
        comment_objects = models.comment_list.objects.filter(thiscomment=thisanswer).all().order_by("-comment_time")
        comment_num = comment_objects.count()

        see_num = thisanswer.see_num
        see_num = see_num + 1
        models.ans_list.objects.filter(id=nid).update(see_num=see_num)

        if thisanswer in commenter.vote_ans.all():
            status = True
        else:
            status = False
        ans_dict = {
            "answer": thisanswer, 
            "problem": problem_object,
            "vote_num": vote_num,
            "comment_num": comment_num,
            "comments": comment_objects,
            "status": status,
            "user_id": commenter_id
        }
        return render(request, "answer_page.html", ans_dict)
    models.comment_list.objects.create(comment_content=comment, thiscomment=thisanswer, commenter=commenter)
    return redirect(f'/{pid}/problem/{nid}/answer')



@csrf_exempt
def answer_agree(request):
    answer_id = request.POST.get("answer_id")
    user_id = request.session['info']['id']
    user_object = models.user_list.objects.filter(id=user_id).first()
    answer_object = models.ans_list.objects.filter(id=answer_id).first()
    user_object.vote_ans.add(answer_object)

    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def answer_agree_cancel(request):
    answer_id = request.POST.get("answer_id")
    user_id = request.session['info']['id']
    user_object = models.user_list.objects.filter(id=user_id).first()
    answer_object = models.ans_list.objects.filter(id=answer_id).first()
    user_object.vote_ans.remove(answer_object)
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))


@csrf_exempt
def problem_follow(request):
    problem_id = request.POST.get("problem_id")
    problem_object = models.ask_list.objects.filter(id=problem_id).first()
    user_id = request.session['info']['id']
    user_object = models.user_list.objects.filter(id=user_id).first()
    user_object.focus_ask.add(problem_object)
    
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def problem_follow_cancel(request):
    problem_id = request.POST.get("problem_id")
    problem_object = models.ask_list.objects.filter(id=problem_id).first()
    user_id = request.session['info']['id']
    user_object = models.user_list.objects.filter(id=user_id).first()
    user_object.focus_ask.remove(problem_object)
    
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))

@csrf_exempt
def index_recommend(request):
    print(request.POST)
    data_dict = {'status': True}
    return HttpResponse(json.dumps(data_dict))
