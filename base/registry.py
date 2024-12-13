subject_choices = [
    ("all", "All")
]

def register_subject_choices(choices):
    if isinstance(choices, list):
        subject_choices.extend(choices)
    else:
        raise ValueError("Choices must be a list of tuples.")

def get_subject_choices(filter_by=None):
    if filter_by == 'ALL' or filter_by is None:
        return subject_choices
    elif filter_by:
        # Assuming `filter_by` matches the first element of the tuple
        return [choice for choice in subject_choices if choice[0] == filter_by]
    else:
        raise ValueError("Invalid filter provided.")