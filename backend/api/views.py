from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from users.models import User
from recipes.models import Tag, Ingredient, Recipe
from .serializers import (
    CustomUserSerializer,
    TagSerializer,
    RecipeSerializer
)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient',
            'tags'
        ).all()
        return recipes

