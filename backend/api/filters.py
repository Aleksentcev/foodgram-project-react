from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(filters.FilterSet):
    pass
