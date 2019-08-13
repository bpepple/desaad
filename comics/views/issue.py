from django.views.generic import DetailView, ListView

from comics.models import Issue

PAGINATE = 28


class IssueList(ListView):
    model = Issue
    paginate_by = PAGINATE
    queryset = Issue.objects.select_related("series")
