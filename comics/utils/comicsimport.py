import logging
import os
import re
from base64 import standard_b64encode
from datetime import datetime

from django.utils import timezone
from django.utils.text import slugify

from comics.comicapi.comicarchive import ComicArchive, MetaDataStyle
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
from comics.utils.metrontalker import MetronTalker


def get_recursive_filelist(pathlist):
    # Get a recursive list of all files under all path items in the list.
    filelist = []
    if os.path.isdir(pathlist):
        for root, _, files in os.walk(pathlist):
            for f in files:
                filelist.append(os.path.join(root, f))
    return filelist


class Importer(object):
    def __init__(self, auth):
        # Configure Logging
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.logger = logging.getLogger("desaad")

        # TODO: Use SETTINGS variable for this.
        self.directory_path = "/home/bpepple/Downloads/Test"

        # Metron creditials
        self.auth = standard_b64encode(auth.encode("utf-8"))

        # Comic tag style
        self.style = MetaDataStyle.CIX

    def create_publish_date(self, day, month, year):
        pub_date = None
        if year is not None:
            try:
                new_day = 1
                new_month = 1
                if month is not None:
                    new_month = int(month)
                if day is not None:
                    new_day = int(day)
                new_year = int(year)
                pub_date = datetime(new_year, new_month, new_day)
            finally:
                pass

        return pub_date

    def check_if_removed_or_modified(self, comic, pathlist):
        remove = False

        def in_folder_list(filepath, pathlist):
            for p in pathlist:
                if p in filepath:
                    return True
            return False

        if not (os.path.exists(comic.file)):
            self.logger.info(f"Removing missing {comic.file}")
            remove = True
        elif not inFolderlist(comic.file, pathlist):
            self.logger.info(f"Removing unwanted {comic.file}")
            remove = True
        else:
            current_timezone = timezone.get_current_timezone()
            c = datetime.utcfromtimestamp(os.path.getmtime(comic.file))
            curr = timezone.make_aware(c, current_timezone)
            prev = comic.mod_ts

            if curr != prev:
                self.logger.info(f"Removing modified {comic.file}")
                remove = True

        if remove:
            # TODO: Add removal code here.
            pass

    def get_comic_metadata(self, path):
        ca = ComicArchive(path)
        if ca.seemsToBeAComicArchive():
            self.logger.info(f"Reading in {self.read_count} {path}")
            self.read_count += 1
            if ca.hasMetadata(self.style):
                md = ca.readMetadata(self.style)
                md.path = ca.path
                md.page_count = ca.page_count
                md.mod_ts = datetime.utcfromtimestamp(os.path.getmtime(ca.path))
                return md
            else:
                return None
        else:
            return None

    def get_metron_issue_id(self, md):
        mid = None
        if md.notes is not None:
            mid = re.search(r"\d+]", md.notes)
            if mid is not None:
                mid = str(mid.group(0))
                mid = mid[:-1]

        return mid

    def get_publisher_obj(self, pub_id, talker):
        pub_obj, create = Publisher.objects.get_or_create(mid=int(pub_id))
        if create:
            # Geet the publisher data
            pub_data = talker.fetch_publisher_data(pub_id)

            pub_obj.name = pub_data["name"]
            pub_obj.slug = slugify(pub_data["name"])
            pub_obj.desc = pub_data["desc"]
            pub_obj.founded = pub_data["founded"]
            # TODO: Save the publisher image
            pub_obj.save()
            print(f"Added publisher: {pub_obj}")

        return pub_obj

    def get_series_obj(self, series_id, talker):
        series_obj, create = Series.objects.get_or_create(mid=int(series_id))
        if create:
            # Get the series detail
            series_data = talker.fetch_series_data(series_id)
            # Get the series type
            series_type_obj, create = SeriesType.objects.get_or_create(
                mid=int(series_data["series_type"]["id"]),
                name=series_data["series_type"]["name"],
            )
            print(f"Series Type: {series_type_obj} Created: {create}")

            series_obj.name = series_data["name"]
            series_obj.slug = slugify(
                series_data["name"] + " " + str(series_data["year_began"])
            )
            series_obj.sort_name = series_data["sort_name"]
            series_obj.volume = series_data["volume"]
            series_obj.year_began = series_data["year_began"]
            series_obj.year_end = series_data["year_end"]
            series_obj.desc = series_data["desc"]
            series_obj.save()
            print(f"Added series: {series_obj}")

        return series_obj

    def add_comic_from_metadata(self, talker, md):
        if not md.isEmpty:
            # Retrieve the Metron issue id from the comic file's tagged info
            mid = self.get_metron_issue_id(md)
            if not mid:
                self.logger.info(
                    f"No Metron ID for: {md.series} #{md.number}... skipping"
                )

            # Let's get the issue data
            issue_data = talker.fetch_issue_data(mid)
            if issue_data is None:
                return False

            # Now the publisher information
            pub_id = issue_data["publisher"]["id"]
            pub_obj = self.get_publisher_obj(pub_id, talker)

            # Now add the series info.
            series_id = issue_data["series"]["id"]
            series_obj = self.get_series_obj(series_id, talker)

            # Now let's create the issue
            current_timezone = timezone.get_current_timezone()
            tz = timezone.make_aware(md.mod_ts, current_timezone)

    def commit_metadata_list(self, md_list):
        talker = MetronTalker(self.auth)
        for md in md_list:
            self.add_comic_from_metadata(talker, md)

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
            if f in filelist:
                filelist.remove(f)

        comics_path = None

        md_list = []
        self.read_count = 0
        for filename in filelist:
            md = self.get_comic_metadata(filename)
            if md is not None:
                md_list.append(md)

            if self.read_count % 100 == 0 and self.read_count != 0:
                if len(md_list) > 0:
                    self.commit_metadata_list(md_list)

        if len(md_list) > 0:
            self.commit_metadata_list(md_list)

        self.logger.info("Finished importing..")
