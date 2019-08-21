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
