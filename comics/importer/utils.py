import os
import uuid
from datetime import datetime


def create_date_path():
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day

    date = (
        os.sep + f"{year:04}" + os.sep + f"{month:02}" + os.sep + f"{day:02}" + os.sep
    )

    return date


def check_for_directories(path):
    head, _ = os.path.split(path)
    if not os.path.isdir(head):
        os.makedirs(head)
        print(f"Created directory: {head}")


def new_image_name(path):
    img_file = os.path.basename(str(path))
    (_, ext) = os.path.splitext(img_file)
    new_filename = str(uuid.uuid4())

    return new_filename + ext


def create_arc_image_path(path):
    file_name = new_image_name(path)
    date_str = create_date_path()
    path = "arcs" + date_str + file_name

    return path


def create_character_image_path(path):
    file_name = new_image_name(path)
    date_str = create_date_path()
    path = "characters" + date_str + file_name

    return path


def create_creator_image_path(path):
    file_name = new_image_name(path)
    date_str = create_date_path()
    path = "creators" + date_str + file_name

    return path


def create_issues_image_path(path):
    file_name = new_image_name(path)
    date_str = create_date_path()
    path = "issues" + date_str + file_name

    return path


def create_publisher_image_path(path):
    file_name = new_image_name(path)
    date_str = create_date_path()
    path = "publishers" + date_str + file_name

    return path


def create_team_image_path(path):
    file_name = new_image_name(path)
    date_str = create_date_path()
    path = "teams" + date_str + file_name

    return path
