from tabnanny import verbose
from django.db import models

# Create your models here.

class ask_list(models.Model):
    asker = models.ForeignKey(to="user_list", to_field="id", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="问题题目", max_length=128)
    ask_intro = models.TextField(verbose_name="问题简介")
    ask_time = models.DateTimeField(auto_now_add=True)
    ask_choices = (
        (1, "学习"),
        (2, "生活"),
        (3, "吐槽"),
        (4, "选课")
    )   # 这是django中的约束
    ask_kind = models.SmallIntegerField(verbose_name="问题标签", choices=ask_choices, null=True, blank=True)
    def __str__(self):
        return self.title
        
class ans_list(models.Model):
    ans_content = models.TextField(verbose_name="回答文本")
    author = models.ForeignKey(to="user_list", to_field="id", on_delete=models.CASCADE)
    thisask = models.ForeignKey(to="ask_list", to_field="id", on_delete=models.CASCADE)
    ans_time = models.DateTimeField(auto_now_add=True)
    see_num = models.IntegerField(verbose_name="浏览量", default=0)
    def __str__(self):
        return self.ans_content[0:40]

class comment_list(models.Model):
    comment_content = models.CharField(verbose_name="评论", max_length=200)
    thiscomment = models.ForeignKey(to="ans_list", to_field="id", on_delete=models.CASCADE)
    commenter = models.ForeignKey(to="user_list", to_field="id", on_delete=models.CASCADE)  
    comment_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.comment_content[0:40]

class user_list(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)
    email = models.CharField(verbose_name="邮箱", max_length=64)
    intro = models.CharField(verbose_name="个人简介", max_length=200, null=True, blank=True)
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )   # 这是django中的约束
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices)
    academy = (
        (2, "电子信息工程学院"),
        (6, "计算机学院"),
        (21, "软件学院"),
    )
    academy = models.SmallIntegerField(verbose_name="学院", choices=academy, default=21)
    vote_ans = models.ManyToManyField(ans_list, verbose_name="赞同回答", null=True, blank=True)
    focus_ask = models.ManyToManyField(ask_list, verbose_name="关注问题", null=True, blank=True)
    def __str__(self):
        return self.name
