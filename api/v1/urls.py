from django.urls import path

from api.v1.auth.views import AuthView, ActionViews
from api.v1.category.views import CategoryView
from api.v1.product.views import ProductView

urlpatterns = [
    path("auth/", AuthView.as_view()),

    path("category/", CategoryView.as_view()),
    path("category/<int:pk>/", CategoryView.as_view()),

    path("product/", ProductView.as_view()),
    path("product/<int:pk>/", ProductView.as_view()),

    path("action/", ActionViews.as_view())
]