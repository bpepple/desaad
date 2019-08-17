from django.urls import path

from comics.views.issue import IssueList

app_name = "issue"
urlpatterns = [path("", IssueList.as_view(), name="list")]
