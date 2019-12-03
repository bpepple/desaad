import operator
from functools import reduce

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from comics.models import Issue, Team

PAGINATE = 28


class TeamList(ListView):
    model = Team
    paginate_by = PAGINATE
    queryset = Team.objects.prefetch_related("issue_set")


class TeamIssueList(ListView):
    paginate_by = PAGINATE
    template_name = "comics/issue_list.html"

    def get_queryset(self):
        team = get_object_or_404(Team, slug=self.kwargs["slug"])
        return Issue.objects.select_related("series").filter(teams=team)


class TeamDetail(DetailView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super(TeamDetail, self).get_context_data(**kwargs)
        team = self.get_object()
        try:
            next_team = Team.objects.filter(name__gt=team.name).order_by("name").first()
        except ObjectDoesNotExist:
            next_team = None

        try:
            previous_team = (
                Team.objects.filter(name__lt=team.name).order_by("name").last()
            )
        except ObjectDoesNotExist:
            previous_team = None

        context["navigation"] = {"next_team": next_team, "previous_team": previous_team}
        return context


class SearchTeamList(TeamList):
    def get_queryset(self):
        result = super(SearchTeamList, self).get_queryset()
        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_, (Q(name__icontains=q) for q in query_list))
            )

        return result
