from django.test import TestCase

from comics.comicapi.genericmetadata import GenericMetadata
from comics.importer.importcomics import ComicImporter
from comics.models import Creator


class TestComicImporter(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.comic_import = ComicImporter()
        cls.creator = Creator.objects.create(
            mid=1, name="John Byrne", slug="john-byrne",
        )

    # TODO: Add test for the issue slug when the issue already exists in the database.
    def test_create_issue_slug(self):
        expected = "batman-2016-005"
        result = self.comic_import.create_issue_slug("batman-2016", 5)
        self.assertEqual(expected, result)

    def test_create_creator_slug(self):
        expected = "walter-simonson"
        result = self.comic_import.create_creator_slug("Walter Simonson")
        self.assertEqual(expected, result)

    def test_create_creator_slug_with_existing_record(self):
        expected = "john-byrne-1"
        result = self.comic_import.create_creator_slug("John Byrne")
        self.assertEqual(expected, result)

    def test_get_metron_issue_id(self):
        meta_data = GenericMetadata()
        meta_data.notes = "Tagged with MetronTagger-0.9.0 using info from Metron on 2019-11-28 12:54:15. [issue_id:7614]"
        expected = "7614"
        result = self.comic_import.get_metron_issue_id(meta_data)
        self.assertEqual(expected, result)
