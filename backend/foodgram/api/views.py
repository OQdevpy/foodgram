from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.db.models import Sum
from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from .filters import IngredientFilter

from posts.models import (IngredientsRecipe, Tag, Ingredient, Recipe,
                          Favorite, ShoppingCard, Subscribe)
from api import serializers
from rest_framework.permissions import IsAuthenticated
# from api.permission import AdminOrReadOnly, AuthorOrReadOnly

from api.utils import (create_model_instance, delete_model_instance)

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
    pagination_class = None
    filter_backends = (filters.SearchFilter,DjangoFilterBackend )
    filterset_class = IngredientFilter
    search_fields = ('^name',)


    


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('author', 'ingredients', 'name', 'cooking_time', )
    # permission_classes = (AuthorOrReadOnly)
    search_fields = ('^name', )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.RecipeReadSerializer
        return serializers.RecipeWriteSerializer

    def get_queryset(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return Recipe.objects.all().prefetch_related(
                'author',
                'ingredients',
                'tags',
            ).distinct()

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart:
            return Recipe.objects.filter(carts__user=self.request.user)

        tags = self.request.query_params.getlist('tags')
        return Recipe.objects.filter(tags__slug__in=tags).prefetch_related(
            'author',
            'ingredients',
            'tags',
        ).distinct()

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated, ),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = IngredientsRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
    
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        """Работа со списком покупок.
        Удаление/добавление в список покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = request.data
            data['recipe'] = recipe.id
            data['user'] = request.user.id
            card = ShoppingCard.objects.filter(user=request.user,
                                               recipe=recipe)
            if card.exists():
                return Response({'errors': 'Рецепт уже в корзине'},
                                status=status.HTTP_400_BAD_REQUEST)
            card = ShoppingCard.objects.create(recipe=recipe,user = request.user)
            serializer = serializers.ShoppingCartSerializer(card)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в списке покупок'
            card = ShoppingCard.objects.filter(user=request.user,
                                               recipe=recipe)
            if not card.exists():
                return Response({'errors': error_message},
                                status=status.HTTP_400_BAD_REQUEST)
            card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        data['author'] = request.user.id
        ingredientss = data.get('ingredients')
        if 'ingredients' in data:
            ingredients = data.pop('ingredients')
            ingredients_ids = [ingredient['id'] for ingredient in ingredients]
            data['ingredients'] = ingredients_ids

        serializer = self.get_serializer(instance, data=request.data,context = {'ingredients':ingredientss, 'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['author'] = request.user.id
        ingredientss = data.get('ingredients')
        if 'ingredients' in data:
            ingredients = data.pop('ingredients')
            ingredients_ids = [ingredient['id'] for ingredient in ingredients]
            data['ingredients'] = ingredients_ids

        serializer = self.get_serializer(data=request.data,context = {'ingredients':ingredientss, 'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
        


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
        serializer = serializers.SubcribeList(qs, many=True,context = {'request': request})
        return Response({'results':serializer.data, 'count':self.get_queryset().count()})

class FavoriteListView(ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = serializers.FavoriteSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        fvs =Favorite.objects.filter(user=self.request.user).values_list('recipe', flat=True)
        return Recipe.objects.filter(id__in=fvs)
    
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = serializers.RecipeReadSerializer(qs, many=True,context = {'request': request})
        return Response({'results':serializer.data, 'count':self.get_queryset().count()})