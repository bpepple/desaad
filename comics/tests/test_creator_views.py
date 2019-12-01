from django.test import TestCase
from django.urls import reverse

from comics.models import Creator

HTML_OK_CODE = 200
HTML_REDIRECT_CODE = 302

PAGINATE_TEST_VAL = 35
PAGINATE_DEFAULT_VAL = 28
PAGINATE_DIFF_VAL = PAGINATE_TEST_VAL - PAGINATE_DEFAULT_VAL


class CreatorSearchViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for pub_num in range(PAGINATE_TEST_VAL):
            Creator.objects.create(
                mid=pub_num, name=f"John-Smith-{pub_num}", slug=f"john-smith-{pub_num}",
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/creator/search")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("creator:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("creator:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/creator_list.html")

    def test_pagination_is_twenty_eight(self):
        resp = self.client.get("/creator/search?q=smith")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["creator_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_all_creators(self):
        # Get second page and confirm it has (exactly) remaining 7 items
        resp = self.client.get("/creator/search?page=2&q=smith")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["creator_list"]) == PAGINATE_DIFF_VAL)


class CreatorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for pub_num in range(PAGINATE_TEST_VAL):
            Creator.objects.create(
                mid=pub_num, name=f"John-Smith-{pub_num}", slug=f"john-smith-{pub_num}",
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/creator/")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("creator:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("creator:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/creator_list.html")

    def test_pagination_is_twenty_eight(self):
        resp = self.client.get(reverse("creator:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["creator_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_second_page(self):
        # Get second page and confirm it has (exactly) remaining 7 items
        resp = self.client.get(reverse("creator:list") + "?page=2")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["creator_list"]) == PAGINATE_DIFF_VAL)


class CreatorDetailViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        slug = "john-smith"
        cls.creator = Creator.objects.create(mid=1, name="John Smith", slug=slug,)

    def test_view_url_accessible_by_name(self):
        url = reverse("creator:detail", args=(self.creator.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        url = reverse("creator:detail", args=(self.creator.slug,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/creator_detail.html")
