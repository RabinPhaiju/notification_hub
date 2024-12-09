from django.contrib import admin

# Register your models here.
from .models import ForumPost,ForumPostReply

admin.site.register(ForumPost)
admin.site.register(ForumPostReply)