"""desaad URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from comics.urls import arc as arc_urls
from comics.urls import character as character_urls
from comics.urls import creator as creator_urls
from comics.urls import home as home_urls
from comics.urls import issue as issue_urls
from comics.urls import publisher as publisher_urls
from comics.urls import series as series_urls
from comics.urls import team as team_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("arc/", include(arc_urls)),
    path("character/", include(character_urls)),
    path("creator/", include(creator_urls)),
    path("", include(home_urls)),
    path("issue/", include(issue_urls)),
    path("publisher/", include(publisher_urls)),
    path("series/", include(series_urls)),
    path("team/", include(team_urls)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
