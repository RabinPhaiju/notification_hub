from django.db import models

class ForumNotificationSubject(models.TextChoices):
    NEW_POST = "new_post", "New Post"
    POST_REPLY = "post_reply", "Post Reply"
    POST_REACTION = "post_reaction", "Post Reaction"

class AuthNotificationSubject(models.TextChoices):
    LOGIN = "login", "Login"
    SIGNUP = "signup", "Signup"

class DefaultNotificationSubject(models.TextChoices):
    ALL = "all", "All"

class NotificationSubject:
    choices = (DefaultNotificationSubject.choices + ForumNotificationSubject.choices + AuthNotificationSubject.choices)

class EssentialNotificationSubject:
    choices = (ForumNotificationSubject.choices + AuthNotificationSubject.choices)