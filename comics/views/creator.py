import operator
from functools import reduce

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from comics.models import Creator, Credits, Issue, Series

PAGINATE = 28


class CreatorList(ListView):
    model = Creator
    paginate_by = PAGINATE
    queryset = Creator.objects.prefetch_related("credits_set")


class CreatorDetail(DetailView):
    model = Creator

    def get_context_data(self, **kwargs):
        context = super(CreatorDetail, self).get_context_data(**kwargs)
        creator = self.get_object()
        qs = Creator.objects.order_by("name")
        try:
            next_creator = qs.filter(name__gt=creator.name).first()
        except ObjectDoesNotExist:
            next_creator = None

        try:
            previous_creator = qs.filter(name__lt=creator.name).last()
        except ObjectDoesNotExist:
            previous_creator = None

        context["navigation"] = {
            "next_creator": next_creator,
            "previous_creator": previous_creator,
        }

        series_issues = (
            Credits.objects.filter(creator=creator)
            .values(
                "issue__series__name",
                "issue__series__year_began",
                "issue__series__slug",
            )
            .annotate(Count("issue"))
            .order_by("issue__series__sort_name", "issue__series__year_began")
        )
        context["credits"] = series_issues

        return context


class CreatorSeriesList(ListView):
    paginate_by = PAGINATE
    template_name = "comicsdb/issue_list.html"

    def get_queryset(self):
        series = get_object_or_404(Series, slug=self.kwargs["series"])
        creator = get_object_or_404(Creator, slug=self.kwargs["creator"])
        return Issue.objects.select_related("series").filter(
            creators=creator, series=series
        )


class CreatorIssueList(ListView):
    paginate_by = PAGINATE
    template_name = "comicsdb/issue_list.html"

    def get_queryset(self):
        creator = get_object_or_404(Creator, slug=self.kwargs["slug"])
        return Issue.objects.select_related("series").filter(creators=creator)


class SearchCreatorList(CreatorList):
    def get_queryset(self):
        result = super(SearchCreatorList, self).get_queryset()
        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_,
                    (
                        # Unaccent lookup won't work on alias array field.
                        Q(name__unaccent__icontains=q) | Q(alias__icontains=q)
                        for q in query_list
                    ),
                )
            )

        return result
