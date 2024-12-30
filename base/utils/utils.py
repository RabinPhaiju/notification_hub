import yaml
from jinja2 import Template,Environment,FileSystemLoader
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ..models import NotificationAttribute,NotificationAttributeAdapter,UserNotificationSetting,NotificationSubjectAll,NotificationSubscriber,Notification
from django.conf import settings
from django.core.mail import EmailMessage

def get_model_attributes(obj,subject):
    try:
        model_name = f'{obj._meta.app_label}.{obj.__class__.__name__}'
        model_data = settings.NOTIFICATION_MODEL_DATA.get(model_name)

        if model_data:
            model_data_paths = [f'data/{path}' for path in model_data]
            data = load_multiple_yaml(model_data_paths).get(subject)
        else: # Fallback to loading a single YAML file
            yaml_path = f'data/{obj.__class__.__name__}.yaml'
            data = load_yaml(yaml_path).get(subject)

        if data is None:
            raise ValueError(f"Subject '{subject}' not found in YAML data for model: {model_name}")
    except AttributeError as e:
        raise AttributeError(f"Error accessing object meta or class: {e}")
    except KeyError as e:
        raise KeyError(f"Error accessing 'subject' in YAML data: {e}")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"YAML file(s) not found: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")

    email_template_path = data.get('email_template_path',None)
    email_template = data.get('email_template',None)

    return NotificationAttribute(
        title=data['title'],
        body=data['body'],
        image_url=data.get('image_url',None),
        email_template = email_template or get_template(email_template_path),
        push_data = data.get('push_data',None),
    )

def load_yaml(file_path):
    try:
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise exc
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found")

def load_multiple_yaml(file_paths):
    combined_data = {}
    for file_path in file_paths:
        yaml_data = load_yaml(file_path)
        if yaml_data:
            combined_data.update(yaml_data)
    return combined_data

def get_user_not_in_group_all(model):
    content_type = ContentType.objects.get_for_model(model)
    return User.objects.filter(
            ~Q(notification_settings__content_type=content_type),
        )

def create_notification_settings(model, subjects=[NotificationSubjectAll.ALL]):
    users_to_create = get_user_not_in_group_all(model)
    if users_to_create.exists():
        content_type = ContentType.objects.get_for_model(model)
        notification_to_create = [
            UserNotificationSetting(user=user, subject=subject, content_type=content_type)
            for user in users_to_create
            for subject in subjects
        ]
        UserNotificationSetting.objects.bulk_create(notification_to_create)
 
def format_message(template,context):
    return Template(template).render(context)

def get_template(template_name):
    env = Environment(loader=FileSystemLoader('templates'))
    return env.loader.get_source(env, template_name)[0]

def format_template(template_name,context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)

def add_subscriber(user_id, model, object_id):
    user = User.objects.get(id=user_id)
    if user:
        content_type = ContentType.objects.get_for_model(model)
        notificationSubs = NotificationSubscriber.objects.filter(
            content_type=content_type,
            generic_object_id=object_id
        ).first()
        
        if notificationSubs: # and user not in notificationSubs.subscribers.all():
            notificationSubs.subscribers.add(user)
            return f'{user.username} added successfully.'
        else:
            return 'No subscribers found.'

def remove_subscriber(user_id, model, object_id):
    user = User.objects.get(id=user_id)
    if user:
        content_type = ContentType.objects.get_for_model(model)
        notificationSubs = NotificationSubscriber.objects.filter(
            content_type=content_type,
            generic_object_id=object_id
        ).first()
        
        if notificationSubs:
            notificationSubs.subscribers.remove(user)
            return f'{user.username} removed successfully.'
        else: 
            return 'No subscribers found.'
        
def convert_notifications_to_email_messages(notification_attributes):
    return [notification_attribute_to_email_message(na) for na in notification_attributes]

def notification_attribute_to_email_message(naa):
    if isinstance(naa, NotificationAttributeAdapter):
        subject = naa.attribute.title
        body = naa.attribute.email_template if naa.attribute.email_template != '' else naa.attribute.body
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipient_emails = [naa.user.email]
        
        # Create an EmailMessage instance
        msg = EmailMessage(subject, body, sender_email, recipient_emails)
        msg.content_subtype = "html"
        
        # Retrieve the attachments from the Attachment model using the provided IDs
        attachment_ids = [naa.attribute.email_attachment_id]
        # for attachment_id in attachment_ids:
        #     try:
        #         attachment = Attachment.objects.get(id=attachment_id)
        #         msg.attach_file(attachment.file.path)  # Use the file's path on the disk
        #     except Attachment.DoesNotExist:
        #         print(f"Attachment with ID {attachment_id} not found.")
        
        return msg
    else:
        raise ValueError("NotificationAttribute is not valid.")

def convert_notifications_to_cloud_messages(notification_attributes):
    return [notification_attribute_to_cloud_message(na) for na in notification_attributes]

def notification_attribute_to_cloud_message(naa):
    if isinstance(naa, NotificationAttributeAdapter):
        return {
            'user': naa.user,
            'title': naa.attribute.title,
            'body': naa.attribute.body,
            'data': naa.attribute.push_data,
        }
    else:
        raise ValueError("NotificationAttribute is not valid.")

def convert_notifications_to_in_app_messages(notification_attributes):
    return [notification_attribute_to_in_app_message(na) for na in notification_attributes]

def notification_attribute_to_in_app_message(naa):
    if isinstance(naa, NotificationAttributeAdapter):
        return Notification(
            user=naa.user,
            title=naa.attribute.title,
            body=naa.attribute.body,
            data=naa.attribute.push_data,
            action_link=naa.attribute.action_link,
            image_url=naa.attribute.image_url,
        )
    else:
        raise ValueError("NotificationAttribute is not valid.")