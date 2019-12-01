from django.test import TestCase
from django.urls import reverse

from comics.models import Publisher, Series, SeriesType

HTML_OK_CODE = 200

PAGINATE_TEST_VAL = 35
PAGINATE_DEFAULT_VAL = 28
PAGINATE_DIFF_VAL = PAGINATE_TEST_VAL - PAGINATE_DEFAULT_VAL


class SeriesSearchViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.publisher = Publisher.objects.create(name="DC", slug="dc", mid=1)
        series_type = SeriesType.objects.create(name="Ongoing Series", mid=1)
        for pub_num in range(PAGINATE_TEST_VAL):
            Series.objects.create(
                mid=pub_num,
                name=f"Series {pub_num}",
                slug=f"series-{pub_num}",
                sort_name=f"Series {pub_num}",
                year_began=2018,
                publisher=cls.publisher,
                volume=f"{pub_num}",
                series_type=series_type,
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/series/search")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("series:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("series:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/series_list.html")

    def test_pagination_is_twenty_eight(self):
        resp = self.client.get("/series/search?q=seri")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["series_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_all_series(self):
        # Get second page and confirm it has (exactly) remaining 5 items
        resp = self.client.get("/series/search?page=2&q=ser")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["series_list"]) == PAGINATE_DIFF_VAL)


class SeriesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        publisher = Publisher.objects.create(name="DC", slug="dc", mid=1)
        series_type = SeriesType.objects.create(name="Ongoing Series", mid=1)
        for pub_num in range(PAGINATE_TEST_VAL):
            Series.objects.create(
                mid=pub_num,
                name=f"Series {pub_num}",
                slug=f"series-{pub_num}",
                sort_name=f"Series {pub_num}",
                year_began=2018,
                publisher=publisher,
                volume=f"{pub_num}",
                series_type=series_type,
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/series/")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("series:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("series:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/series_list.html")

    def test_pagination_is_twenty_eight(self):
        resp = self.client.get(reverse("series:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["series_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_second_page(self):
        # Get second page and confirm it has (exactly) remaining 7 items
        resp = self.client.get(reverse("series:list") + "?page=2")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["series_list"]) == PAGINATE_DIFF_VAL)


class SeriesDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pub = Publisher.objects.create(mid=1, name="DC Comics", slug="dc-comics")

        cls.series = Series.objects.create(
            mid=5, publisher=pub, name="Superman", slug="superman"
        )

    def test_view_url_accessible_by_name(self):
        url = reverse("series:detail", args=(self.series.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        url = reverse("series:detail", args=(self.series.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/series_detail.html")
