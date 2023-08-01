import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import User, Subscribe
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientRecipe,
    Favorite,
    ShoppingCart,
    TagRecipe,
)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
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


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        fields = ('id', 'name', 'color', 'slug',)
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit',)
        model = Ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount',)
        model = IngredientRecipe


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ('id', 'amount',)
        model = IngredientRecipe


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('is_favorited', 'is_in_shopping_cart',)
        model = Recipe

    def check_recipe(self, model, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return model.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False

    def get_is_favorited(self, obj):
        return self.check_recipe(model=Favorite, obj=obj)

    def get_is_in_shopping_cart(self, obj):
        return self.check_recipe(model=ShoppingCart, obj=obj)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    def create_ingredients_recipe(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipe=recipe
            )

    def create_tags_recipe(self, tags, recipe):
        for tag in tags:
            TagRecipe.objects.create(
                tag_id=tag.id,
                recipe=recipe
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=author)
        self.create_ingredients_recipe(ingredients, recipe)
        self.create_tags_recipe(tags, recipe)
        return recipe


class RecipeCutSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time',)
        model = Recipe


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        fields = (
            'username',
            'id',
            'password',
            'email',
            'first_name',
            'last_name',
        )
        model = User


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeCutSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
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
