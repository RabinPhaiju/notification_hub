import yaml
from jinja2 import Template,Environment,FileSystemLoader
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from base.models import NotificationAttribute
from django.conf import settings
from base.enums import NotificationTypes

def get_model_attributes(obj,subject):
    model_name = obj.__class__.__name__
    email_template_path = get_model_template_path(NotificationTypes.EMAIL.value,obj)
    email_template = get_template(email_template_path)
    data = load_yaml(f'data/{NotificationTypes.EMAIL.value}/{model_name}.yaml')[subject]

    return NotificationAttribute(
        title=format_message(data['title'],{'obj':obj}),
        body=format_message(data['body'],{'obj':obj}),
        email_html = email_template,
        push_data = data['push_data'] ,
    )

def load_yaml(file_path):
    try:
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise exc
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found")

def get_user_not_in_group_all(model):
    content_type = ContentType.objects.get_for_model(model)
    return User.objects.filter(
            ~Q(notification_settings__content_type=content_type),
        )

def format_message(template,context):
    return Template(template).render(context)

def get_template(template_name):
    env = Environment(loader=FileSystemLoader('templates'))
    return env.loader.get_source(env, template_name)[0]

def format_template(template_name,context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)

def get_model_template_path(type,model):
    model_path = f"{model._meta.app_label}.{model.__class__.__name__}"
    return settings.NOTIFICATION_MODEL_TEMPLATE_PATHS.get(type).get(model_path)