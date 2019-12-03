import operator
from functools import reduce

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from comics.models import Arc, Issue

PAGINATE = 28


class ArcList(ListView):
    model = Arc
    paginate_by = PAGINATE
    queryset = Arc.objects.prefetch_related("issue_set")


class ArcIssueList(ListView):
    template_name = "comics/issue_list.html"
    paginate_by = PAGINATE

    def get_queryset(self):
        arc = get_object_or_404(Arc, slug=self.kwargs["slug"])
        return Issue.objects.select_related("series").filter(arcs=arc)


class ArcDetail(DetailView):
    model = Arc
    queryset = Arc.objects.prefetch_related(
        Prefetch(
            "issue_set",
            queryset=Issue.objects.order_by(
                "cover_date", "store_date", "series__sort_name", "number"
            ).select_related("series"),
        )
    )

    def get_context_data(self, **kwargs):
        context = super(ArcDetail, self).get_context_data(**kwargs)
        arc = self.get_object()
        try:
            next_arc = Arc.objects.order_by("name").filter(name__gt=arc.name).first()
        except ObjectDoesNotExist:
            next_arc = None

        try:
            previous_arc = Arc.objects.order_by("name").filter(name__lt=arc.name).last()
        except ObjectDoesNotExist:
            previous_arc = None

        context["navigation"] = {"next_arc": next_arc, "previous_arc": previous_arc}
        return context


class SearchArcList(ArcList):
    def get_queryset(self):
        result = super(SearchArcList, self).get_queryset()
        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_, (Q(name__icontains=q) for q in query_list))
            )

        return result
