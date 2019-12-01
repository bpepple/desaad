from django.test import TestCase
from django.urls import reverse

from comics.models import Publisher

HTML_OK_CODE = 200

PAGINATE_TEST_VAL = 35
PAGINATE_DEFAULT_VAL = 28
PAGINATE_DIFF_VAL = PAGINATE_TEST_VAL - PAGINATE_DEFAULT_VAL


class PublisherSearchViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for pub_num in range(PAGINATE_TEST_VAL):
            Publisher.objects.create(
                mid=pub_num,
                name="Publisher %s" % pub_num,
                slug="publisher-%s" % pub_num,
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/publisher/search")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("publisher:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("publisher:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/publisher_list.html")

    def test_pagination_is_twenty_eight(self):
        resp = self.client.get("/publisher/search?q=pub")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["publisher_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_all_publishers(self):
        # Get second page and confirm it has (exactly) remaining 7 items
        resp = self.client.get("/publisher/search?page=2&q=pub")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["publisher_list"]) == PAGINATE_DIFF_VAL)


class PublisherListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for pub_num in range(PAGINATE_TEST_VAL):
            Publisher.objects.create(
                mid=pub_num,
                name="Publisher %s" % pub_num,
                slug="publisher-%s" % pub_num,
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/publisher/")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("publisher:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("publisher:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/publisher_list.html")

    def test_pagination_is_twenty_eight(self):
        resp = self.client.get(reverse("publisher:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["publisher_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_second_page(self):
        # Get second page and confirm it has (exactly) remaining 7 items
        resp = self.client.get(reverse("publisher:list") + "?page=2")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["publisher_list"]) == PAGINATE_DIFF_VAL)
