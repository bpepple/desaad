from django.urls import path

from comics.views.issue import IssueDetail, IssueList

app_name = "issue"
urlpatterns = [
    path("", IssueList.as_view(), name="list"),
    path("<slug:slug>/", IssueDetail.as_view(), name="detail"),
]
