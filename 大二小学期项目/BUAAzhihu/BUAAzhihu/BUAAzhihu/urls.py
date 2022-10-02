"""BUAAzhihu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1.views import user, index
urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', user.login),
    path('register/', user.register),
    path('logout/', user.logout),
    path('<int:nid>/ask/raise', user.ask),
    path('<int:nid>/homepage', user.self_homepage),

    path('ask/delete', user.ask_delete),
    path('ans/delete', user.ans_delete),
    path('agree/delete', user.agree_delete),
    path('focus/delete', user.focus_delete),
    path('focus/delete', user.focus_delete),
    path('ask/edit', user.ask_edit),
    path('ask/edit/confirm', user.ask_edit_confirm),
    path('ans/edit', user.ans_edit),
    path('ans/edit/confirm', user.ans_edit_confirm),

    path('index/', index.show_homepage),
    path('problem/set', index.problem_set),
    path('<int:nid>/problem', index.problem_page),
    path('index/recommend/', index.index_recommend),
    path('<int:pid>/problem/<int:nid>/answer', index.answer_page),

    path('answer/agree/', index.answer_agree),
    path('answer/agree/cancel/', index.answer_agree_cancel),
    path('problem/follow/', index.problem_follow),
    path('problem/follow/cancel/', index.problem_follow_cancel),

]
