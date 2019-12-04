from django.urls import path

from comics.views.home import HomePageView

app_name = ""
urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
