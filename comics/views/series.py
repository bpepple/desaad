import operator
from functools import reduce

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from comics.models import Issue, Series

PAGINATE = 28


class SeriesList(ListView):
    model = Series
    paginate_by = PAGINATE
    queryset = Series.objects.prefetch_related("issue_set")


class SeriesIssueList(ListView):
    template_name = "comics/issue_list.html"
    paginate_by = PAGINATE

    def get_queryset(self):
        series = get_object_or_404(Series, slug=self.kwargs["slug"])
        return Issue.objects.select_related("series").filter(series=series)


class SeriesDetail(DetailView):
    model = Series
    queryset = Series.objects.select_related("publisher").prefetch_related("issue_set")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.get_object()

        # Set the initial value for the navigation variables
        next_series = None
        previous_series = None

        # Create the base queryset with all the series.
        qs = Series.objects.all().order_by("name", "year_began")

        # Determine if there is more than 1 series with the same name
        series_count = qs.filter(name__gte=series.name).count()

        # If there is more than one series with the same name
        # let's attempt to get the next and previous items
        if series_count > 1:
            try:
                next_series = qs.filter(
                    name=series.name, year_began__gt=series.year_began
                ).first()
            except ObjectDoesNotExist:
                next_series = None

            try:
                previous_series = qs.filter(
                    name=series.name, year_began__lt=series.year_began
                ).last()
            except ObjectDoesNotExist:
                previous_series = None

        if not next_series:
            try:
                next_series = qs.filter(name__gt=series.name).first()
            except ObjectDoesNotExist:
                next_series = None

        if not previous_series:
            try:
                previous_series = qs.filter(name__lt=series.name).last()
            except ObjectDoesNotExist:
                previous_series = None

        context["navigation"] = {
            "next_series": next_series,
            "previous_series": previous_series,
        }
        return context


class SearchSeriesList(SeriesList):
    def get_queryset(self):
        result = super(SearchSeriesList, self).get_queryset()
        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_, (Q(name__icontains=q) for q in query_list))
            )

        return result
