from django.urls import path, re_path

from comics.views.series import (
    SearchSeriesList,
    SeriesDetail,
    SeriesIssueList,
    SeriesList,
)

app_name = "series"
urlpatterns = [
    path("", SeriesList.as_view(), name="list"),
    path("<slug:slug>/", SeriesDetail.as_view(), name="detail"),
    path("<slug:slug>/issue_list/", SeriesIssueList.as_view(), name="issue"),
    re_path(r"^search/?$", SearchSeriesList.as_view(), name="search"),
]
