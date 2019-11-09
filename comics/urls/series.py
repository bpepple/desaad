from django.urls import path

from comics.views.series import SeriesDetail, SeriesIssueList, SeriesList

app_name = "series"
urlpatterns = [
    path("", SeriesList.as_view(), name="list"),
    path("<slug:slug>/", SeriesDetail.as_view(), name="detail"),
    path("<slug:slug>/issue_list/", SeriesIssueList.as_view(), name="issue"),
]
