from darkseid.genericmetadata import GenericMetadata
from django.test import TestCase
from django.utils import timezone

from comics.importer.importcomics import ComicImporter
from comics.models import Character, Creator, Issue, Publisher, Series, Team


class TestComicImporter(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.comic_import = ComicImporter()

        cover_date = timezone.now().date()
        mod_time = timezone.now()

        cls.publisher = Publisher.objects.create(
            mid=5, name="DC Comics", slug="dc-comics"
        )
        series = Series.objects.create(
            mid=5,
            publisher=cls.publisher,
            name="Superman",
            slug="superman-2016",
            year_began="2016",
        )
        Issue.objects.create(
            mid="4321",
            slug="superman-2016-001",
            file="/home/b.cbz",
            mod_ts=mod_time,
            cover_date=cover_date,
            number="1",
            series=series,
        )
        Creator.objects.create(mid=1, name="John Byrne", slug="john-byrne")
        Character.objects.create(mid=5, name="Human Torch", slug="human-torch")
        Team.objects.create(mid=2, name="Teen Titans", slug="teen-titans")

    def test_create_team_slug(self):
        expected = "avengers"
        result = self.comic_import.create_team_slug("Avengers")
        self.assertEqual(expected, result)

    def test_create_team_slug_with_existing_record(self):
        expected = "teen-titans-1"
        result = self.comic_import.create_team_slug("Teen Titans")
        self.assertEqual(expected, result)

    def test_create_issue_slug(self):
        expected = "batman-2016-005"
        result = self.comic_import.create_issue_slug("batman-2016", 5)
        self.assertEqual(expected, result)

    def test_create_issue_slug_with_existing_record(self):
        expected = "superman-2016-001-1"
        result = self.comic_import.create_issue_slug("superman-2016", 1)
        self.assertEqual(expected, result)

    def test_create_series_slug(self):
        expected = "batman-2016"
        result = self.comic_import.create_series_slug("batman", 2016)
        self.assertEqual(expected, result)

    def test_create_series_slug_with_existing_record(self):
        expected = "superman-2016-1"
        result = self.comic_import.create_series_slug("superman", 2016)
        self.assertEqual(expected, result)

    def test_create_creator_slug(self):
        expected = "walter-simonson"
        result = self.comic_import.create_creator_slug("Walter Simonson")
        self.assertEqual(expected, result)

    def test_create_creator_slug_with_existing_record(self):
        expected = "john-byrne-1"
        result = self.comic_import.create_creator_slug("John Byrne")
        self.assertEqual(expected, result)

    def test_create_character_slug(self):
        expected = "black-bolt"
        result = self.comic_import.create_character_slug("Black Bolt")
        self.assertEqual(expected, result)

    def test_create_character_slug_with_existing_record(self):
        expected = "human-torch-1"
        result = self.comic_import.create_character_slug("Human Torch")
        self.assertEqual(expected, result)

    def test_get_metron_issue_id(self):
        meta_data = GenericMetadata()
        meta_data.notes = "Tagged with MetronTagger-0.9.0 using info from Metron on 2019-11-28 12:54:15. [issue_id:7614]"
        expected = "7614"
        result = self.comic_import.get_metron_issue_id(meta_data)
        self.assertEqual(expected, result)

    def test_get_publisher_obj_existing(self):
        result = self.comic_import.get_publisher_obj(self.publisher.mid)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, self.publisher.name)
