from django.urls import path, re_path

from comics.views.publisher import (
    PublisherDetail,
    PublisherList,
    PublisherSeriesList,
    SearchPublisherList,
)

app_name = "publisher"
urlpatterns = [
    path("", PublisherList.as_view(), name="list"),
    path("<slug:slug>/", PublisherDetail.as_view(), name="detail"),
    path("<slug:slug>/series_list/", PublisherSeriesList.as_view(), name="series"),
    re_path(r"^search/?$", SearchPublisherList.as_view(), name="search"),
]
