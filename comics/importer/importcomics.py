import itertools
import logging
import os
import re
from base64 import standard_b64encode
from datetime import datetime

from darkseid.comicarchive import ComicArchive
from darkseid.issuestring import IssueString
from django.db import IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from comics.importer.metrontalker import MetronTalker
from comics.importer.utils import (
    check_for_directories,
    create_arc_image_path,
    create_character_image_path,
    create_creator_image_path,
    create_issues_image_path,
    create_publisher_image_path,
    create_team_image_path,
)
from comics.models import (
    Arc,
    Character,
    Creator,
    Credits,
    Issue,
    Publisher,
    Role,
    Series,
    SeriesType,
    Team,
)
from desaad.settings import MEDIA_ROOT, METRON_PASS, METRON_USER

LOGGER = logging.getLogger(__name__)


def get_recursive_filelist(pathlist):
    # Get a recursive list of all files under all path items in the list.
    filelist = []
    if os.path.isdir(pathlist):
        for root, _, files in os.walk(pathlist):
            for comic in files:
                filelist.append(os.path.join(root, comic))
    return filelist


class ComicImporter:
    def __init__(self):
        # TODO: Use SETTINGS variable for this.
        self.directory_path = "/home/bpepple/Documents/Comics"

        # Metron creditials
        creditials = f"{METRON_USER}:{METRON_PASS}"
        self.auth = standard_b64encode(creditials.encode("utf-8"))

        # Count of issues imported into the database
        self.read_count = 0

        # Metron Talker object
        self.talker = None

    @staticmethod
    def create_issue_slug(series, number):
        formatted_number = IssueString(number).as_string(pad=3)
        slug = orig = slugify(f"{series}-{formatted_number}")

        for count in itertools.count(1):
            if not Issue.objects.filter(slug=slug).exists():
                break
            slug = f"{orig}-{count}"

        return slug

    @staticmethod
    def create_series_slug(series, year):
        slug = orig = slugify(f"{series}-{year}")

        for count in itertools.count(1):
            if not Series.objects.filter(slug=slug).exists():
                break
            slug = f"{orig}-{count}"

        return slug

    @staticmethod
    def create_creator_slug(name):
        slug = orig = slugify(name)

        for count in itertools.count(1):
            if not Creator.objects.filter(slug=slug).exists():
                break
            slug = f"{orig}-{count}"

        return slug

    @staticmethod
    def create_character_slug(name):
        slug = orig = slugify(name)

        for count in itertools.count(1):
            if not Character.objects.filter(slug=slug).exists():
                break
            slug = f"{orig}-{count}"

        return slug

    @staticmethod
    def create_team_slug(name):
        slug = orig = slugify(name)

        for count in itertools.count(1):
            if not Team.objects.filter(slug=slug).exists():
                break
            slug = f"{orig}-{count}"

        return slug

    @staticmethod
    def check_if_removed_or_modified(comic, pathlist):
        remove = False

        def in_folder_list(filepath, pathlist):
            for f_file in pathlist:
                if f_file in filepath:
                    return True
            return False

        existing = os.path.exists(comic.file)
        if not existing:
            LOGGER.info(f"Removing missing {comic.file}")
            remove = True
        elif not in_folder_list(comic.file, pathlist):
            LOGGER.info(f"Removing unwanted {comic.file}")
            remove = True
        else:
            current_timezone = timezone.get_current_timezone()
            current_date = datetime.utcfromtimestamp(os.path.getmtime(comic.file))
            curr = timezone.make_aware(current_date, current_timezone)
            prev = comic.mod_ts

            if curr != prev:
                LOGGER.info(f"Removing modified {comic.file}")
                remove = True

        if remove:
            series = Series.objects.get(id=comic.series.id)
            count = series.issue_count
            if count == 1:
                series.delete()
                LOGGER.info(f"Removing series: {series}")
            else:
                comic.delete()

    def get_comic_metadata(self, path):
        meta_data = None
        comic_archive = ComicArchive(path)
        if comic_archive.seems_to_be_a_comic_archive():
            LOGGER.info(f"Reading in {self.read_count} {path}")
            self.read_count += 1
            if comic_archive.has_metadata():
                meta_data = comic_archive.read_metadata()
                meta_data.path = comic_archive.path
                meta_data.page_count = comic_archive.page_count
                meta_data.mod_ts = datetime.utcfromtimestamp(
                    os.path.getmtime(comic_archive.path)
                )

        return meta_data

    @staticmethod
    def get_metron_issue_id(meta_data):
        mid = None
        if meta_data.notes is not None:
            mid = re.search(r"\d+]", meta_data.notes)
            if mid is not None:
                mid = str(mid.group(0))
                mid = mid[:-1]

        return mid

    def fetch_publisher_image(self, image):
        # Path and new file name to save in the database.
        img_db_path = create_publisher_image_path(image)
        # Path to save in the filesystem
        img_save_path = MEDIA_ROOT + os.sep + img_db_path
        # Create the filesystem path if it doesn't exist.
        check_for_directories(img_save_path)
        # Finally, let's actually fetch the image.
        self.talker.fetch_image(image, img_save_path)

        return img_db_path

    def get_publisher_obj(self, pub_id):
        pub_obj, create = Publisher.objects.get_or_create(mid=int(pub_id))
        if create:
            # Geet the publisher data
            pub_data = self.talker.fetch_publisher_data(pub_id)

            pub_obj.name = pub_data["name"]
            pub_obj.slug = slugify(pub_data["name"])
            pub_obj.desc = pub_data["desc"]
            pub_obj.founded = pub_data["founded"]
            pub_obj.wikipedia = pub_data["wikipedia"]

            # If there is a publisher image, fetch it.
            if pub_data["image"] is not None:
                pub_obj.image = self.fetch_publisher_image(pub_data["image"])

            pub_obj.save()
            LOGGER.info(f"Added publisher: {pub_obj}")

        return pub_obj

    def get_series_obj(self, series_id):
        series_obj, create = Series.objects.get_or_create(mid=int(series_id))
        if create:
            # Get the series detail
            series_data = self.talker.fetch_series_data(series_id)

            # Get the Publisher
            pub_id = series_data["publisher"]
            pub_obj = self.get_publisher_obj(pub_id)

            # Get the series type
            series_type_obj, create = SeriesType.objects.get_or_create(
                mid=int(series_data["series_type"]["id"]),
                name=series_data["series_type"]["name"],
            )

            series_obj.name = series_data["name"]
            series_obj.slug = self.create_series_slug(
                series_data["name"], series_data["year_began"]
            )
            series_obj.sort_name = series_data["sort_name"]
            series_obj.volume = series_data["volume"]
            series_obj.year_began = series_data["year_began"]
            series_obj.year_end = series_data["year_end"]
            series_obj.desc = series_data["desc"]
            series_obj.series_type = series_type_obj
            series_obj.publisher = pub_obj
            series_obj.save()
            LOGGER.info(f"Added series: {series_obj}")

        return series_obj

    def fetch_arc_image(self, image):
        # Path and new file name to save in the database.
        img_db_path = create_arc_image_path(image)
        # Path to save in the filesystem
        img_save_path = MEDIA_ROOT + os.sep + img_db_path
        # Create the filesystem path if it doesn't exist.
        check_for_directories(img_save_path)
        # Finally, let's actually fetch the image.
        self.talker.fetch_image(image, img_save_path)

        return img_db_path

    def get_arc_obj(self, arc_id):
        arc_obj, create = Arc.objects.get_or_create(mid=int(arc_id))
        if create:
            # Get arc detail
            arc_data = self.talker.fetch_arc_data(arc_id)
            arc_obj.name = arc_data["name"]
            arc_obj.slug = slugify(arc_data["name"])
            arc_obj.desc = arc_data["desc"]
            # If there is a creator image, fetch it.
            if arc_data["image"] is not None:
                arc_obj.image = self.fetch_arc_image(arc_data["image"])
            arc_obj.save()
            LOGGER.info(f"Added arc: {arc_obj}")

        return arc_obj

    def fetch_creator_image(self, image):
        # Path and new file name to save in the database.
        img_db_path = create_creator_image_path(image)
        # Path to save in the filesystem
        img_save_path = MEDIA_ROOT + os.sep + img_db_path
        # Create the filesystem path if it doesn't exist.
        check_for_directories(img_save_path)
        # Finally, let's actually fetch the image.
        self.talker.fetch_image(image, img_save_path)

        return img_db_path

    def get_creator_obj(self, creator_id):
        creator_obj, create = Creator.objects.get_or_create(mid=int(creator_id))
        if create:
            # Get the creator data
            creator_data = self.talker.fetch_creator_data(creator_id)

            # Save data the doesn't neeed to be massaged
            creator_obj.name = creator_data["name"]
            creator_obj.slug = self.create_creator_slug(creator_data["name"])
            creator_obj.desc = creator_data["desc"]
            creator_obj.wikipedia = creator_data["wikipedia"]

            # If there is a creator image, fetch it.
            if creator_data["image"] is not None:
                creator_obj.image = self.fetch_creator_image(creator_data["image"])

            # Convert date of birth to datetime if present
            if creator_data["birth"] is not None:
                creator_obj.birth = datetime.strptime(creator_data["birth"], "%Y-%m-%d")

            # Convert date of death to datetime if present
            if creator_data["death"] is not None:
                creator_obj.death = datetime.strptime(creator_data["death"], "%Y-%m-%d")

            creator_obj.save()
            LOGGER.info(f"Added Creator: {creator_obj}")

        return creator_obj

    def fetch_team_image(self, image):
        # Path and new file name to save in the database.
        img_db_path = create_team_image_path(image)
        # Path to save in the filesystem
        img_save_path = MEDIA_ROOT + os.sep + img_db_path
        # Create the filesystem path if it doesn't exist.
        check_for_directories(img_save_path)
        # Finally, let's actually fetch the image.
        self.talker.fetch_image(image, img_save_path)

        return img_db_path

    def get_team_obj(self, team_id):
        team_obj, create = Team.objects.get_or_create(mid=int(team_id))
        if create:
            team_data = self.talker.fetch_team_data(team_id)

            team_obj.name = team_data["name"]
            team_obj.slug = self.create_team_slug(team_data["name"])
            team_obj.desc = team_data["desc"]
            team_obj.wikipedia = team_data["wikipedia"]

            if team_data["image"] is not None:
                team_obj.image = self.fetch_team_image(team_data["image"])

            if team_data["creators"] is not None:
                for creator in team_data["creators"]:
                    person = self.get_creator_obj(creator["id"])
                    team_obj.creators.add(person)
                    LOGGER.info(f"Added Creator to {team_obj}")

            team_obj.save()
            LOGGER.info(f"Added Team: {team_obj}")

        return team_obj

    def fetch_character_image(self, image):
        # Path and new file name to save in the database.
        img_db_path = create_character_image_path(image)
        # Path to save in the filesystem
        img_save_path = MEDIA_ROOT + os.sep + img_db_path
        # Create the filesystem path if it doesn't exist.
        check_for_directories(img_save_path)
        # Finally, let's actually fetch the image.
        self.talker.fetch_image(image, img_save_path)

        return img_db_path

    def get_character_obj(self, character_id):
        character_obj, create = Character.objects.get_or_create(mid=int(character_id))
        if create:
            character_data = self.talker.fetch_character_data(character_id)

            character_obj.name = character_data["name"]
            character_obj.slug = self.create_character_slug(character_data["name"])
            character_obj.desc = character_data["desc"]
            character_obj.wikipedia = character_data["wikipedia"]

            if character_data["image"] is not None:
                character_obj.image = self.fetch_character_image(
                    character_data["image"]
                )

            if character_data["alias"] is not None:
                character_obj.alias = character_data["alias"]

            if character_data["creators"] is not None:
                for creator in character_data["creators"]:
                    creator_obj = self.get_creator_obj(creator["id"])
                    character_obj.creators.add(creator_obj)
                    LOGGER.info(f"Added Creator to {character_obj}")

            if character_data["teams"] is not None:
                for team in character_data["teams"]:
                    team_obj = self.get_team_obj(team["id"])
                    character_obj.teams.add(team_obj)
                    LOGGER.info(f"Added Team to {character_obj}")

            character_obj.save()
            LOGGER.info(f"Added Character: {character_obj}")

        return character_obj

    @staticmethod
    def get_role_obj(role):
        role_name = role["name"].title()
        role_id = int(role["id"])
        role_obj, _ = Role.objects.get_or_create(name=role_name, mid=role_id)

        return role_obj

    def fetch_issue_image(self, image):
        img_db_path = create_issues_image_path(image)
        img_save_path = MEDIA_ROOT + os.sep + img_db_path
        check_for_directories(img_save_path)
        self.talker.fetch_image(image, img_save_path)

        return img_db_path

    def add_comic_from_metadata(self, meta_data):
        # Retrieve the Metron issue id from the comic file's tagged info
        mid = self.get_metron_issue_id(meta_data)
        if not mid:
            LOGGER.info(
                f"No Metron ID for: {meta_data.series} #{meta_data.number}... skipping"
            )
            return False

        # Let's get the issue data
        issue_data = self.talker.fetch_issue_data(mid)
        if issue_data is None:
            return False

        # Now get the series info.
        series_id = issue_data["series"]["id"]
        series_obj = self.get_series_obj(series_id)

        # Now let's create the issue
        current_timezone = timezone.get_current_timezone()
        t_zone = timezone.make_aware(meta_data.mod_ts, current_timezone)

        if issue_data["cover_date"] is not None:
            cover_date = datetime.strptime(issue_data["cover_date"], "%Y-%m-%d")

        issue_slug = self.create_issue_slug(series_obj.slug, meta_data.issue)
        try:
            issue_obj = Issue.objects.create(
                file=meta_data.path,
                mid=int(issue_data["id"]),
                number=issue_data["number"],
                slug=issue_slug,
                name=issue_data["name"],
                cover_date=cover_date,
                desc=issue_data["desc"],
                page_count=meta_data.page_count,
                mod_ts=t_zone,
                series=series_obj,
            )
        except IntegrityError as i_error:
            LOGGER.error(f"Attempting to create issue in database - {i_error}")
            LOGGER.info(f"Skipping: {meta_data.path}")
            return False

        LOGGER.info(f"Created {issue_obj}")

        # Fetch the issue image
        if issue_data["image"] is not None:
            issue_obj.image = self.fetch_issue_image(issue_data["image"])
            issue_obj.save()

        # If there is a store date, let's add it to the issue.
        if issue_data["store_date"] is not None:
            issue_obj.store_date = datetime.strptime(
                issue_data["store_date"], "%Y-%m-%d"
            )
            issue_obj.save()

        # Add any arcs to the issue.
        for arc in issue_data["arcs"]:
            if arc:
                arc_obj = self.get_arc_obj(arc["id"])
                if arc_obj:
                    issue_obj.arcs.add(arc_obj)

        # Add any characters to the issue.
        for character in issue_data["characters"]:
            if character:
                character_obj = self.get_character_obj(character["id"])
                if character_obj:
                    issue_obj.characters.add(character_obj)

        # Add any teams to the issue.
        for team in issue_data["teams"]:
            if team:
                team_obj = self.get_team_obj(team["id"])
                if team_obj:
                    issue_obj.teams.add(team_obj)

        # Add any creator credits to the issue
        for credit in issue_data["credits"]:
            if credit:
                creator_id = credit["id"]
                creator_obj = self.get_creator_obj(creator_id)
                credit_obj, _ = Credits.objects.get_or_create(
                    issue=issue_obj, creator=creator_obj
                )
                roles = credit["role"]
                for role in roles:
                    role_obj = self.get_role_obj(role)
                    credit_obj.role.add(role_obj)

                LOGGER.info(f"Added credit for {creator_obj} to {issue_obj}")

        return True

    def commit_metadata_list(self, md_list):
        self.talker = MetronTalker(self.auth)
        for meta_data in md_list:
            self.add_comic_from_metadata(meta_data)

    def import_comics(self):
        filelist = get_recursive_filelist(self.directory_path)
        filelist = sorted(filelist, key=os.path.getmtime)

        # Get a list of all the issues in the db
        comics = Issue.objects.all()

        # Remove from the db any missing or changed  files
        for comic in comics:
            self.check_if_removed_or_modified(comic, self.directory_path)

        comics = None

        # Reload the issues again to take into account any issues removed from the db
        # TODO: Can probably remove any issues in the prior loop, but let's improve it later.
        comics = Issue.objects.all()

        # Make a list of all the path string in the db.
        comics_path = []
        for comic in comics:
            comics_path.append(comic.file)

        comics = None

        # Now let's remove any existing files in the db from the directory list of files.
        for comic_path in comics_path:
            if comic_path in filelist:
                filelist.remove(comic_path)

        comics_path = None

        md_list = []
        for filename in filelist:
            meta_data = self.get_comic_metadata(filename)
            if meta_data is not None:
                md_list.append(meta_data)

            if self.read_count % 100 == 0 and self.read_count != 0:
                if len(md_list) > 0:
                    self.commit_metadata_list(md_list)

        if len(md_list) > 0:
            self.commit_metadata_list(md_list)

        LOGGER.info("Finished importing..")
