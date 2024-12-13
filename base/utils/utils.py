import yaml
from jinja2 import Template,Environment,FileSystemLoader
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from base.models import NotificationAttribute
from django.conf import settings

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

def format_message(template,context):
    return Template(template).render(context)

def get_template(template_name):
    env = Environment(loader=FileSystemLoader('templates'))
    return env.loader.get_source(env, template_name)[0]

def format_template(template_name,context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)
