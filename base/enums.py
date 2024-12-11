from enum import Enum

class NotifyTarget(Enum):
    ALL = 'all'
    SUBSCRIBERS = 'subscribers'
    NEWSLETTER = 'newsletter'
    NEWSLETTER_EMAIL = 'newsletter_email'
    OTHER = 'other'
    
class NotificationTypes(Enum):
    NOTIFICATIONS_ENABLED = 'notifications_enabled'
    EMAIL = 'email'
    PUSH_NOTIFICATION = 'push_notification'
    IN_APP = 'in_app'