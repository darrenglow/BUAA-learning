from django.contrib import admin

# Register your models here.

from app1.models import comment_list, user_list, ask_list, ans_list
# admin.site.register(user_list)
admin.site.register(ask_list)
admin.site.register(ans_list)
admin.site.register(comment_list)

class userInline(admin.TabularInline):
    model = user_list.focus_ask.through

class userInline2(admin.TabularInline):
    model = user_list.vote_ans.through

@admin.register(user_list)
class userAdmin(admin.ModelAdmin):
    inlines = (userInline, userInline2,)
    exclude = ('focus_ask', 'vote_ans',)