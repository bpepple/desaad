from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from django.views.generic import DetailView, ListView

from comics.models import Credits, Issue

PAGINATE = 28


class IssueList(ListView):
    model = Issue
    paginate_by = PAGINATE
    queryset = Issue.objects.select_related("series")


class IssueDetail(DetailView):
    model = Issue
    queryset = Issue.objects.select_related(
        "series", "series__publisher"
    ).prefetch_related(
        Prefetch(
            "credits_set",
            queryset=Credits.objects.order_by("creator__name")
            .distinct("creator__name")
            .select_related("creator")
            .prefetch_related("role"),
        )
    )

    def get_context_data(self, **kwargs):
        context = super(IssueDetail, self).get_context_data(**kwargs)
        issue = self.get_object()
        try:
            next_issue = issue.get_next_by_cover_date(series=issue.series)
        except ObjectDoesNotExist:
            next_issue = None

        try:
            previous_issue = issue.get_previous_by_cover_date(series=issue.series)
        except ObjectDoesNotExist:
            previous_issue = None

        context["navigation"] = {
            "next_issue": next_issue,
            "previous_issue": previous_issue,
        }
        return context
