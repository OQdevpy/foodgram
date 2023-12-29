import django_filters
from django_filters import rest_framework as filters
from django.db import models

from posts.models import Ingredient, Recipe

class IngredientFilter(filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Ingredient
        fields = ['name', 'measurement_unit']