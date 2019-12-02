from django.urls import path, re_path

from comics.views.character import (
    CharacterDetail,
    CharacterIssueList,
    CharacterList,
    CharacterSeriesList,
    SearchCharacterList,
)

app_name = "character"
urlpatterns = [
    path("", CharacterList.as_view(), name="list"),
    path("<slug:slug>/", CharacterDetail.as_view(), name="detail"),
    path("<slug:slug>/issue_list/", CharacterIssueList.as_view(), name="issue"),
    path(
        "<slug:character>/<slug:series>/", CharacterSeriesList.as_view(), name="series"
    ),
    re_path(r"^search/?$", SearchCharacterList.as_view(), name="search"),
]
