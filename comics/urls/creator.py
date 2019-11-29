from django.urls import path, re_path

from comics.views.creator import (
    CreatorDetail,
    CreatorIssueList,
    CreatorList,
    CreatorSeriesList,
    SearchCreatorList,
)

app_name = "creator"
urlpatterns = [
    path("", CreatorList.as_view(), name="list"),
    path("<slug:slug>/", CreatorDetail.as_view(), name="detail"),
    path("<slug:slug>/issue_list/", CreatorIssueList.as_view(), name="issue"),
    path("<slug:creator>/<slug:series>/", CreatorSeriesList.as_view(), name="series"),
    re_path(r"^search/?$", SearchCreatorList.as_view(), name="search"),
]
