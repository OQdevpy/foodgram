import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer
                                as DjoserUserCreateSerializer)

from posts.models import (Tag, Ingredient, Recipe, IngredientsRecipe,
                          Favorite, ShoppingCard, Subscribe)
from posts import validators


User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password',
                  'first_name', 'last_name',)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=(validators.validate_username, ),
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = fields = '__all__'


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    measurement_unit = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'measurement_unit')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True,
    )
    ingredients = IngredientRecipeSerializer(
        read_only=True,
        many=True
    )
    tags = TagSerializer(
        read_only=True,
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return f"http://159.89.106.151:9000{obj.image.url}"

    class Meta:
        fields = ('id', 'author', 'ingredients', 'tags',
                  'name', 'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart','image')
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        user_object = get_object_or_404(User, username=user)
        return Favorite.objects.filter(user=user_object, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        user_object = get_object_or_404(User, username=user)
        return ShoppingCard.objects.filter(user=user_object,
                                           recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'author', 'ingredients', 'tags',
                  'name', 'text', 'cooking_time', 'image')
        model = Recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        image_data = validated_data.pop('image')
        image_content = image_data.read()
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe.ingredients.set(ingredients_data)
        recipe.image.save(image_data.name, ContentFile(
                          base64.b64decode(image_content)))
        return recipe
    
  
    def update(self, instance, validated_data):
        ingredients_data =  validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.tags.set(tags_data)
        instance.ingredients.set(ingredients_data)
        instance.save()
        return instance


class SubscribeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('author', 'user')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='recipe.id',
    )
    name = serializers.ReadOnlyField(
        source='recipe.name',
    )
    image = serializers.CharField(
        source='recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time',
    )

    class Meta:
        model = ShoppingCard
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    image = serializers.CharField(
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')




class SubcribeList(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        return RecipeReadSerializer(recipes, many=True,context = {'request':self.context['request']}).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'recipes_count', 'recipes')