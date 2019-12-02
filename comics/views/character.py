import operator
from functools import reduce

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from comics.models import Character, Issue, Series

PAGINATE = 28


class CharacterSeriesList(ListView):
    paginate_by = PAGINATE
    template_name = "comics/issue_list.html"

    def get_queryset(self):
        series = get_object_or_404(Series, slug=self.kwargs["series"])
        character = get_object_or_404(Character, slug=self.kwargs["character"])

        return Issue.objects.select_related("series").filter(
            characters=character, series=series
        )


class CharacterList(ListView):
    model = Character
    paginate_by = PAGINATE
    queryset = Character.objects.prefetch_related("issue_set")


class CharacterIssueList(ListView):
    paginate_by = PAGINATE
    template_name = "comics/issue_list.html"

    def get_queryset(self):
        character = get_object_or_404(Character, slug=self.kwargs["slug"])
        return Issue.objects.select_related("series").filter(characters=character)


class CharacterDetail(DetailView):
    model = Character
    queryset = Character.objects.prefetch_related(
        Prefetch(
            "issue_set",
            queryset=Issue.objects.order_by(
                "series__sort_name", "cover_date", "number"
            ).select_related("series"),
        )
    )

    def get_context_data(self, **kwargs):
        context = super(CharacterDetail, self).get_context_data(**kwargs)
        character = self.get_object()
        qs = Character.objects.order_by("name")
        try:
            next_character = qs.filter(name__gt=character.name).first()
        except ObjectDoesNotExist:
            next_character = None

        try:
            previous_character = qs.filter(name__lt=character.name).last()
        except ObjectDoesNotExist:
            previous_character = None

        # TODO: Look into improving this queryset
        #
        # Run this context queryset if the issue count is greater than 0.
        if character.issue_count:
            series_issues = (
                Character.objects.filter(id=character.id)
                .values(
                    "issue__series__name",
                    "issue__series__year_began",
                    "issue__series__slug",
                )
                .annotate(Count("issue"))
                .order_by("issue__series__sort_name", "issue__series__year_began")
            )
            context["appearances"] = series_issues
        else:
            context["appearances"] = ""

        context["navigation"] = {
            "next_character": next_character,
            "previous_character": previous_character,
        }
        return context


class SearchCharacterList(CharacterList):
    def get_queryset(self):
        result = super(SearchCharacterList, self).get_queryset()
        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_,
                    (Q(name__icontains=q) | Q(alias__icontains=q) for q in query_list),
                )
            )

        return result
