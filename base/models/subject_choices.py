from django.db import models

class ForumNotificationSubject(models.TextChoices):
    NEW_POST = "new_post", "New Post"
    POST_COMMENT = "post_comment", "Post Comment"
    POST_REACTION = "post_reaction", "Post Reaction"

class AuthNotificationSubject(models.TextChoices):
    LOGIN = "login", "Login"
    SIGNUP = "signup", "Signup"

class NotificationSubjectAll(models.TextChoices):
    ALL = "all", "All"
    
class NotificationSubjectChoices:
     choices = NotificationSubjectAll.choices + AuthNotificationSubject.choices + ForumNotificationSubject.choices