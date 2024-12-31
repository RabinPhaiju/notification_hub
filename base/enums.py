from enum import Enum

class NotifyTarget(Enum):
    ALL = 'all'
    TOPIC = 'topic'
    SUBSCRIBERS = 'subscribers'
    NEWSLETTER = 'newsletter'
    NEWSLETTER_EMAIL = 'newsletter_email'
    OTHER = 'other'
    
class NotificationTypes(Enum):
    NOTIFICATIONS_ENABLED = 'notifications_enabled'
    EMAIL = 'email'
    PUSH = 'push'
    IN_APP = 'in_app'