from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r"projects/?",views.Projects.as_view()),
    re_path(r"^project/(?P<pk>[\d]+)/?$",views.Project.as_view()),
    re_path(r"cases/?",views.TestCases.as_view()),
]

