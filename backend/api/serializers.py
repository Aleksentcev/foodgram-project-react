from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import User
from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        )
        model = User


class CustomUserSerializer(UserSerializer):
    class Meta:
        fields = (
            'email',
            'pk',
            'username',
            'first_name',
            'last_name',
        )
        model = User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('pk', 'name', 'color', 'slug')
        model = Tag


class IngredientRecipeSerializer(serializers.ModelSerializer):
    pk = serializers.ReadOnlyField(source='ingredient.pk')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = (
            'pk',
            'name',
            'measurement_unit',
            'amount'
        )
        model = IngredientRecipe


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )

    class Meta:
        fields = (
            'pk',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe
