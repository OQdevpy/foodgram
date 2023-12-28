from django.contrib import admin

from .models import (Ingredient, Recipe, Tag,
                     IngredientsRecipe, Favorite, ShoppingCard, Subscribe)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'image', 'text',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('^name',)


admin.site.register(Favorite)
admin.site.register(IngredientsRecipe)
admin.site.register(ShoppingCard)
admin.site.register(Subscribe)
admin.site.register(Tag)
