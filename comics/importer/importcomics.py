import itertools
import logging
import os
import re
from base64 import standard_b64encode
from datetime import datetime

from django.db import IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from comics.comicapi.comicarchive import ComicArchive, MetaDataStyle
from comics.comicapi.issuestring import IssueString
from comics.importer.metrontalker import MetronTalker
from comics.importer.utils import (
    check_for_directories,
    create_creator_image_path,
    create_issues_image_path,
    create_publisher_image_path,
)
from comics.models import (
    Arc,
    Creator,
    Credits,
    Issue,
    Publisher,
    Role,
    Series,
    SeriesType,
)
from desaad.settings import MEDIA_ROOT, METRON_PASS, METRON_USER


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
        # Configure Logging
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.logger = logging.getLogger("desaad")

        # TODO: Use SETTINGS variable for this.
        self.directory_path = "/home/bpepple/Documents/Comics"

        # Metron creditials
        creditials = f"{METRON_USER}:{METRON_PASS}"
        self.auth = standard_b64encode(creditials.encode("utf-8"))

        # Comic tag style
        self.style = MetaDataStyle.CIX

        # Count of issues imported into the database
        self.read_count = 0

        # Metron Talker object
        self.talker = None

    @staticmethod
    def create_issue_slug(series, number):
        formatted_number = IssueString(number).asString(pad=3)
        slug = orig = slugify(series + "-" + formatted_number)

        for count in itertools.count(1):
            if not Issue.objects.filter(slug=slug).exists():
                break
            slug = f"{orig}-{count}"

        return slug

    @staticmethod
    def create_series_slug(series, year):
        slug = orig = slugify(series + "-" + str(year))

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

    def check_if_removed_or_modified(self, comic, pathlist):
        remove = False

        def in_folder_list(filepath, pathlist):
            for f_file in pathlist:
                if f_file in filepath:
                    return True
            return False

        existing = os.path.exists(comic.file)
        if not existing:
            self.logger.info(f"Removing missing {comic.file}")
            remove = True
        elif not in_folder_list(comic.file, pathlist):
            self.logger.info(f"Removing unwanted {comic.file}")
            remove = True
        else:
            current_timezone = timezone.get_current_timezone()
            current_date = datetime.utcfromtimestamp(os.path.getmtime(comic.file))
            curr = timezone.make_aware(current_date, current_timezone)
            prev = comic.mod_ts

            if curr != prev:
                self.logger.info(f"Removing modified {comic.file}")
                remove = True

        if remove:
            series = Series.objects.get(id=comic.series.id)
            count = series.issue_count
            if count == 1:
                series.delete()
                self.logger.info(f"Removing series: {series}")
            else:
                comic.delete()

    def get_comic_metadata(self, path):
        comic_archive = ComicArchive(path)
        if comic_archive.seemsToBeAComicArchive():
            self.logger.info(f"Reading in {self.read_count} {path}")
            self.read_count += 1
            if comic_archive.hasMetadata(self.style):
                meta_data = comic_archive.readMetadata(self.style)
                meta_data.path = comic_archive.path
                meta_data.page_count = comic_archive.page_count
                meta_data.mod_ts = datetime.utcfromtimestamp(
                    os.path.getmtime(comic_archive.path)
                )
                return meta_data
        else:
            return None

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

            # If there is a publisher image, fetch it.
            if pub_data["image"] is not None:
                pub_obj.image = self.fetch_publisher_image(pub_data["image"])

            pub_obj.save()
            self.logger.info(f"Added publisher: {pub_obj}")

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
            self.logger.info(f"Added series: {series_obj}")

        return series_obj

    def get_arc_obj(self, arc_id):
        arc_obj, create = Arc.objects.get_or_create(mid=int(arc_id))
        if create:
            # Get arc detail
            arc_data = self.talker.fetch_arc_data(arc_id)

            arc_obj.name = arc_data["name"]
            arc_obj.slug = slugify(arc_data["name"])
            arc_obj.desc = arc_data["desc"]
            # TODO: Add arc image
            arc_obj.save()
            self.logger.info(f"Added arc: {arc_obj}")

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
            self.logger.info(f"Added Creator: {creator_obj}")

        return creator_obj

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
        if not meta_data.isEmpty:
            # Retrieve the Metron issue id from the comic file's tagged info
            mid = self.get_metron_issue_id(meta_data)
            if not mid:
                self.logger.info(
                    f"No Metron ID for: {meta_data.series} #{meta_data.number}... skipping"
                )

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
            # TODO: Add title array to issue
            try:
                issue_obj = Issue.objects.create(
                    file=meta_data.path,
                    mid=int(issue_data["id"]),
                    number=issue_data["number"],
                    slug=issue_slug,
                    cover_date=cover_date,
                    desc=issue_data["desc"],
                    page_count=meta_data.page_count,
                    mod_ts=t_zone,
                    series=series_obj,
                )
            except IntegrityError as i_error:
                self.logger.error(f"Attempting to create issue in database - {i_error}")
                self.logger.info(f"Skipping: {meta_data.path}")
                return False

            self.logger.info(f"Created {issue_obj}")

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

                    self.logger.info(f"Added credit for {creator_obj} to {issue_obj}")

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

        self.logger.info("Finished importing..")
