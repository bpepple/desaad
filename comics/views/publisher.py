import operator
from functools import reduce

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from comics.models import Publisher, Series

PAGINATE = 28


class PublisherList(ListView):
    model = Publisher
    paginate_by = PAGINATE
    queryset = Publisher.objects.prefetch_related("series_set")


class PublisherSeriesList(ListView):
    template_name = "comics/series_list.html"
    paginate_by = PAGINATE

    def get_queryset(self):
        pub = get_object_or_404(Publisher, slug=self.kwargs["slug"])
        return Series.objects.filter(publisher=pub).prefetch_related("issue_set")


class PublisherDetail(DetailView):
    model = Publisher
    queryset = Publisher.objects.select_related("edited_by").prefetch_related(
        "series_set"
    )

    def get_context_data(self, **kwargs):
        context = super(PublisherDetail, self).get_context_data(**kwargs)
        publisher = self.get_object()
        try:
            next_publisher = (
                Publisher.objects.order_by("name")
                .filter(name__gt=publisher.name)
                .first()
            )
        except ObjectDoesNotExist:
            next_publisher = None

        try:
            previous_publisher = (
                Publisher.objects.order_by("name")
                .filter(name__lt=publisher.name)
                .last()
            )
        except ObjectDoesNotExist:
            previous_publisher = None

        context["navigation"] = {
            "next_publisher": next_publisher,
            "previous_publisher": previous_publisher,
        }
        return context


class SearchPublisherList(PublisherList):
    def get_queryset(self):
        result = super(SearchPublisherList, self).get_queryset()
        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_, (Q(name__icontains=q) for q in query_list))
            )

        return result
