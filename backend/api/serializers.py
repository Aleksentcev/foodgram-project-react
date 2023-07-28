from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import User, Subscribe
from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe, Favorite


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('pk', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'pk',
            'name',
            'measurement_unit',
        )
        model = Ingredient


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


class RecipeCutSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'pk',
            'name',
            'image',
            'cooking_time',
        )
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'favorite')
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'favorite')
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'pk',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                favorite=obj
            ).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        fields = (
            'username',
            'pk',
            'password',
            'email',
            'first_name',
            'last_name',
        )
        model = User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'pk',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'author')
        model = Subscribe
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author')
            )
        ]


class SubscribeInfoSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeCutSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'pk',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Subscribe.objects.filter(
                user=request.user,
                author=obj
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
