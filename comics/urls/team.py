from django.urls import path, re_path

from comics.views.team import SearchTeamList, TeamDetail, TeamIssueList, TeamList

app_name = "team"
urlpatterns = [
    path("", TeamList.as_view(), name="list"),
    path("<slug:slug>/", TeamDetail.as_view(), name="detail"),
    path("<slug:slug>/issue_list/", TeamIssueList.as_view(), name="issue"),
    re_path(r"^search/?$", SearchTeamList.as_view(), name="search"),
]
