from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from comics.models import Issue, Publisher, Series, SeriesType

HTML_OK_CODE = 200
PAGINATE_TEST_VAL = 35
PAGINATE_DEFAULT_VAL = 28
PAGINATE_DIFF_VAL = PAGINATE_TEST_VAL - PAGINATE_DEFAULT_VAL


class IssueListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cover_date = timezone.now().date()
        mod_time = timezone.now()

        publisher = Publisher.objects.create(name="DC", slug="dc", mid=1)
        series_type = SeriesType.objects.create(name="Ongoing Series", mid=1)
        superman = Series.objects.create(
            mid=1,
            name="Superman",
            slug="superman",
            sort_name="Superman",
            year_began=2018,
            publisher=publisher,
            volume="4",
            series_type=series_type,
        )
        for i_num in range(PAGINATE_TEST_VAL):
            Issue.objects.create(
                mid=i_num,
                series=superman,
                number=i_num,
                slug=f"superman-2018-{i_num}",
                cover_date=cover_date,
                mod_ts=mod_time,
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/issue/")
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("issue:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("issue:list"))
        self.assertEqual(resp.status_code, HTML_OK_CODE)
        self.assertTemplateUsed(resp, "comics/issue_list.html")

    # def test_pagination_is_thirty(self):
    #     resp = self.client.get(reverse("issue:list"))
    #     self.assertEqual(resp.status_code, HTML_OK_CODE)
    #     self.assertTrue("is_paginated" in resp.context)
    #     self.assertTrue(resp.context["is_paginated"] == True)
    #     self.assertTrue(len(resp.context["issue_list"]) == PAGINATE_DEFAULT_VAL)

    # def test_lists_second_page(self):
    #     # Get second page and confirm it has (exactly) remaining 7 items
    #     resp = self.client.get(reverse("issue:list") + "?page=2")
    #     self.assertEqual(resp.status_code, HTML_OK_CODE)
    #     self.assertTrue("is_paginated" in resp.context)
    #     self.assertTrue(resp.context["is_paginated"] == True)
    #     self.assertTrue(len(resp.context["issue_list"]) == PAGINATE_DIFF_VAL)
