from django.urls import path, re_path

from comics.views.arc import ArcDetail, ArcIssueList, ArcList, SearchArcList

app_name = "arc"
urlpatterns = [
    path("", ArcList.as_view(), name="list"),
    path("<slug:slug>/", ArcDetail.as_view(), name="detail"),
    path("<slug:slug>/issue_list/", ArcIssueList.as_view(), name="issue"),
    re_path(r"^search/?$", SearchArcList.as_view(), name="search"),
]
