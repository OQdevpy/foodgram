from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from posts.models import (Tag, Ingredient, Recipe,
                          Favorite, ShoppingCard, Subscribe)
from api import serializers
from rest_framework.permissions import IsAuthenticated
# from api.permission import AdminOrReadOnly, AuthorOrReadOnly


User = get_user_model()


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class TagsViewSet(viewsets.ModelViewSet):
    # permission_classes = (AdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', 'slug')
    search_fields = ('^name',)


class IngredientsViewSet(viewsets.ModelViewSet):
    # permission_classes = (AdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    # filterset_fields = ('name')
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('author', 'ingredients', 'name', 'cooking_time')
    # permission_classes = (AuthorOrReadOnly)
    search_fields = ('^name', )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.RecipeReadSerializer
        return serializers.RecipeWriteSerializer

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'author',
            'ingredients',
            'tags',
        ).all()


class SubcribeCreateDeleteViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SubscribeCreateSerializer

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        if Subscribe.objects.filter(user=self.request.user,
                                    author_id=user_id).exists():
            return Response({'errors': 'Вы уже подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user, author_id=user_id)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=('delete',), detail=True)
    def delete(self, request, author_id):
        deleted_count, _ = Subscribe.objects.filter(user=request.user,
                                                    author_id=author_id
                                                    ).delete()
        if deleted_count == 0:
            return Response({'errors': 'Вы не были подписаны на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    serializer_class = serializers.ShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user.id
        print(user)
        return ShoppingCard.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):

        if ShoppingCard.objects.filter(user=self.request.user,
                                       recipe_id=self.kwargs.get('recipe_id')
                                       ).exists():
            return Response({'errors': 'Рецепт уже в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        user = request.user
        shopping_cards = user.shopping_cart.filter(recipe_id=recipe_id)
        if not shopping_cards.exists():
            return Response({'errors': 'Рецепта нет в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        shopping_cards.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = serializers.FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):

        if Favorite.objects.filter(user=self.request.user,
                                   recipe_id=self.kwargs.get('recipe_id')
                                   ).exists():
            return Response({'errors': 'Рецепт уже в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        user = request.user
        deleted_count, _ = user.favorites.filter(recipe_id=recipe_id).delete()
        if deleted_count == 0:
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(CreateAPIView):
    serializer_class = serializers.UserCreateSerializer
    queryset = User.objects.all()
    # permission_classes = ()

    def create(self, request, *args, **kwargs):
        data = request.data
        sz = self.get_serializer(data=data)
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response(sz.data, status=status.HTTP_201_CREATED)


class SubscribeListView(ListAPIView):
    queryset = Subscribe.objects.all()
    serializer_class = serializers.SubscribeCreateSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        print(self.request.user)
        return Subscribe.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = serializers.SubcribeList(qs, many=True)
        return Response({'results':serializer.data, 'count':self.get_queryset().count()})