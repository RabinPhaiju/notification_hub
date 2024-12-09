from django.db import models

class ForumNotificationSubject(models.TextChoices):
    NEW_POST = "new_post", "New Post"
    POST_EDIT = "post_edit", "Post Edit"
    POST_REACTION = "post_reaction", "Post Reaction"

class ForumReplyNotificationSubject(models.TextChoices):
    NEW_REPLY = "new_reply", "New Reply"
    REPLY_EDIT = "reply_edit", "Reply Edit"
    REPLY_REACTION = "reply_reaction", "Reply Reaction"

class OfferNotificationSubject(models.TextChoices):
    NEW_OFFER = "new_offer", "New Offer"
    OFFER_REMINDER = "offer_reminder", "Offer Reminder"

class AuthNotificationSubject(models.TextChoices):
    LOGIN = "login", "Login"
    SIGNUP = "signup", "Signup"

class NotificationSubjectAll(models.TextChoices):
    ALL = "all", "All"
    
class NotificationSubjectChoices:
     choices = NotificationSubjectAll.choices + AuthNotificationSubject.choices + ForumNotificationSubject.choices