import yaml
import json
from jinja2 import Template,Environment,FileSystemLoader
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from base.models import NotificationAttribute

def get_model_attributes(obj,subject):
    model = obj.__class__.__name__
    if model == 'ForumPost' or model == 'ForumPostReply':
        data = load_yaml(f'data/yaml/{model}.yaml')[subject]
        return NotificationAttribute(
            title=format_message(data['title'],{'obj':obj}),
            body=format_message(data['body'],{'obj':obj}),
            email_html = format_template(data['email_html'],{'obj':obj}),
            push_data = data['push_data'],
        )
    elif model == 'Offer':
        return NotificationAttribute(
            title = obj.title,
            body = obj.body,
            email_html = format_message(obj.email_template,{'obj':obj}),
            push_data = json.dumps({'id':obj.id,'end':str(obj.end)}),
        )

def load_yaml(file_path):
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

def format_message(template,context):
    return Template(template).render(context)

def format_template(template_name,context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)
