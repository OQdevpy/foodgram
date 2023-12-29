from rest_framework.routers import DefaultRouter

from django.urls import include, path

from api.views import (SubscribeListView, TagsViewSet, IngredientsViewSet,
                       RecipeViewSet, FavoriteViewSet,
                       ShoppingCartViewSet,
                       SubcribeCreateDeleteViewSet,FavoriteListView)
from users.views import UserViewSet


router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredient', IngredientsViewSet, basename='ingredient')
router.register('tags', TagsViewSet, basename='tags')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
    basename='favorite')
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet,
    basename='shoppingcart')
router.register('users', UserViewSet, basename='users')

router.register(r'recipe/(?P<user_id>\d+)/recipe',
                SubcribeCreateDeleteViewSet, basename='recipe-create')


urlpatterns = [
    path('subscriptions/', SubscribeListView.as_view(), name='subscribe'),
    path('favourites/', FavoriteListView.as_view(), name='favourites'),
    path('', include(router.urls)),
]
