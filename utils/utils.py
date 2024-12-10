import yaml
import json
from django.apps import apps
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from base.models import NotificationAttribute

def get_model_attributes(obj,subject):
    model = obj.__class__.__name__
    if model == 'ForumPost' or model == 'ForumPostReply':
        data = load_yaml_to_dict(f'data/yaml/{model}.yaml')[subject]
        return NotificationAttribute(
            title = data['title'],
            body = data['body'],
            email_html = data['email_html'],
            push_data = data['push_data'],
        )
    elif model == 'Offer':
        return NotificationAttribute(
            title = obj.title,
            body = obj.body,
            email_html = obj.email_template,
            push_data = json.dumps({'id':obj.id,'end':str(obj.end)}),
        )

def load_yaml_to_dict(file_path):
    try:
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")
        return {}
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {}

def get_user_not_in_group_all(model):
    content_type = ContentType.objects.get_for_model(model)
    return User.objects.filter(
            ~Q(notification_settings__content_type=content_type),
        )
