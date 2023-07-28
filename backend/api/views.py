from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from users.models import User, Subscribe
from recipes.models import Tag, Ingredient, Recipe, Favorite
from .serializers import (
    CustomUserSerializer,
    SubscribeSerializer,
    SubscribeInfoSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCutSerializer,
    FavoriteSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient',
            'tags'
        ).all()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        serializer = FavoriteSerializer(
            data={'user': request.user.pk, 'favorite': recipe.pk}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeCutSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        Favorite.objects.filter(user=request.user, favorite=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        serializer = SubscribeSerializer(
            data={'user': request.user.pk, 'author': author.pk}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = SubscribeInfoSerializer(
                author,
                context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        Subscribe.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)