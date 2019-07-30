import os
from datetime import datetime

from django.utils import timezone

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


def get_recursive_filelist(pathlist):
    # Get a recursive list of all files under all path items in the list.
    filelist = []
    if os.path.isdir(pathlist):
        for root, _, files in os.walk(pathlist):
            for f in files:
                filelist.append(os.path.join(root, f))
    return filelist


class Importer(object):
    def __init__(self):
        self.header = {"user-agent": "desaad"}
        self.baseurl = "https://metron.cloud/api"

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
            series = Series.objects.get(id=comic.series.id)
            s_count = series.issue_count
            # If this is the only issue for a series, delete the series.
            if s_count == 1:
                series.delete()
                self.logger.info(f"Deleting series: {series}")
            else:
                comic.delete()
