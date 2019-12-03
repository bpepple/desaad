from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from comics.models import (
    Arc,
    Character,
    Creator,
    Issue,
    Publisher,
    Role,
    Series,
    SeriesType,
    Team,
)

HTTP_200_OK = 200


class TeamTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = "Justice League"
        cls.slug = slugify(cls.name)
        cls.jl = Team.objects.create(name=cls.name, slug=cls.slug, mid=1)

    def test_test_creation(self):
        self.assertTrue(isinstance(self.jl, Team))
        self.assertEqual(str(self.jl), self.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.jl._meta.verbose_name_plural), "teams")


class CharacterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = "Wonder Woman"
        cls.slug = slugify(cls.name)
        cls.ww = Character.objects.create(name=cls.name, slug=cls.slug, mid=1)

    def test_character_creation(self):
        self.assertTrue(isinstance(self.ww, Character))
        self.assertEqual(str(self.ww), self.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.ww._meta.verbose_name_plural), "characters")


class ArcTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = "The Last Age of Magic"
        cls.slug = slugify(cls.name)

        cls.arc = Arc.objects.create(name=cls.name, slug=cls.slug, mid=1)

    def test_arc_creation(self):
        self.assertTrue(isinstance(self.arc, Arc))
        self.assertEqual(str(self.arc), self.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.arc._meta.verbose_name_plural), "arcs")


class CreatorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = "Walter Simonson"
        cls.slug = "walter-simonson"
        cls.creator = Creator.objects.create(name=cls.name, slug=cls.slug, mid=1)

    def test_creator_creation(self):
        self.assertTrue(isinstance(self.creator, Creator))
        self.assertEqual(str(self.creator), self.name)

    def test_creator_get_full_name(self):
        self.assertEqual(self.creator.name, self.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.creator._meta.verbose_name_plural), "creators")


class RoleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = "writer"
        notes = "Writer of the issues story"
        cls.role = Role.objects.create(name=cls.name, notes=notes, mid=1)

    def test_role_creation(self):
        self.assertTrue(isinstance(self.role, Role))
        self.assertEqual(str(self.role), self.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.role._meta.verbose_name_plural), "roles")


class PublisherTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = "DC Comics"
        cls.slug = slugify(cls.name)

        cls.publisher = Publisher.objects.create(
            name=cls.name, slug=cls.slug, founded=1934, mid=5
        )

        on_going_series = SeriesType.objects.create(name="Ongoing Series", mid=2)

        Series.objects.create(
            name="Superman",
            slug="superman",
            sort_name="Superman",
            series_type=on_going_series,
            publisher=cls.publisher,
            volume=1,
            year_began=1939,
            mid=5,
        )

    def test_series_count(self):
        self.assertEqual(self.publisher.series_count, 1)

    def test_publisher_creation(self):
        self.assertTrue(isinstance(self.publisher, Publisher))
        self.assertEqual(str(self.publisher), self.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.publisher._meta.verbose_name_plural), "publishers")


class SeriesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        publisher = Publisher.objects.create(name="DC Comics", slug="dc-comics", mid=6)
        series_type = SeriesType.objects.create(name="Ongoing Series", mid=5)
        cls.name = "Superman"
        cls.superman = Series.objects.create(
            name=cls.name,
            slug=slugify(cls.name),
            sort_name=cls.name,
            series_type=series_type,
            publisher=publisher,
            volume=1,
            year_began=1939,
            mid=6,
        )

    def test_series_creation(self):
        self.assertTrue(isinstance(self.superman, Series))
        self.assertEqual(str(self.superman), "Superman (1939)")

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.superman._meta.verbose_name_plural), "Series")


class IssueTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        issue_date = timezone.now().date()
        mod_time = timezone.now()

        publisher = Publisher.objects.create(name="DC Comics", slug="dc-comics", mid=8)
        series_type = SeriesType.objects.create(name="Ongoing Series", mid=10)
        cls.series_name = "Superman"
        cls.superman = Series.objects.create(
            name=cls.series_name,
            slug=slugify(cls.series_name),
            sort_name=cls.series_name,
            series_type=series_type,
            publisher=publisher,
            volume=1,
            year_began=1939,
            mid=9,
        )

        cls.issue = Issue.objects.create(
            mid=10,
            series=cls.superman,
            number="1",
            slug="superman-1939-1",
            cover_date=issue_date,
            file="/home/bpepple/test.cbz",
            mod_ts=mod_time,
        )

    def test_issue_creation(self):
        self.assertTrue(isinstance(self.issue, Issue))
        self.assertEqual(str(self.issue), "Superman #1")

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.issue._meta.verbose_name_plural), "issues")

    # This test should be in the SeriesTest but for now let's leave this here.
    def test_issue_count(self):
        issue_count = self.superman.issue_count
        self.assertEqual(issue_count, 1)


class SeriesTypeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = "Mini-Series"
        cls.notes = "A short series typically four issues"

        cls.series_type = SeriesType.objects.create(name=cls.name, notes=cls.notes, mid=5)

    def test_seriestype_creation(self):
        self.assertTrue(isinstance(self.series_type, SeriesType))
        self.assertEqual(str(self.series_type), self.name)
