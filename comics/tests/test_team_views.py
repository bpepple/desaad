from django.test import TestCase
from django.urls import reverse

from comics.models import Team

HTML_OK_CODE = 200

PAGINATE_TEST_VAL = 35
PAGINATE_DEFAULT_VAL = 28
PAGINATE_DIFF_VAL = PAGINATE_TEST_VAL - PAGINATE_DEFAULT_VAL


class TeamSearchViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for pub_num in range(PAGINATE_TEST_VAL):
            Team.objects.create(
                name="Team %s" % pub_num, slug="team-%s" % pub_num, mid=pub_num
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/team/search")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("team:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("team:search"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/team_list.html")

    def test_pagination_is_thirty(self):
        resp = self.client.get("/team/search?q=tea")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["team_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_all_teams(self):
        # Get second page and confirm it has (exactly) remaining 7 items
        resp = self.client.get("/team/search?page=2&q=tea")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["team_list"]) == PAGINATE_DIFF_VAL)


class TeamListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for pub_num in range(PAGINATE_TEST_VAL):
            Team.objects.create(
                name="Team %s" % pub_num, slug="team-%s" % pub_num, mid=pub_num
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/team/")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("team:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("team:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/team_list.html")

    def test_pagination_is_thirty(self):
        resp = self.client.get(reverse("team:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["team_list"]) == PAGINATE_DEFAULT_VAL)

    def test_lists_second_page(self):
        # Get second page and confirm it has (exactly) remaining 7 items
        resp = self.client.get(reverse("team:list") + "?page=2")
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTrue("is_paginated" in resp.context)
        self.assertTrue(resp.context["is_paginated"])
        self.assertTrue(len(resp.context["team_list"]) == PAGINATE_DIFF_VAL)
