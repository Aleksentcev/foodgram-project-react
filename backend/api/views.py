from rest_framework import (
    status,
    viewsets,
    permissions,
    filters,
    exceptions,
    pagination,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from users.models import User, Subscribe
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCutSerializer,
    CustomUserSerializer,
    SubscribeSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # только админ
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


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
        favorite, created = Favorite.objects.select_related(
            'user',
            'favorite'
            ).get_or_create(user=request.user, favorite=recipe)
        if request.method == 'POST' and not created:
            raise exceptions.ValidationError(
                detail='Вы уже добавили рецепт в избранное!'
            )
        if request.method == 'POST':
            serializer = RecipeCutSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        shopping_cart, created = ShoppingCart.objects.select_related(
            'user',
            'shopping_cart'
            ).get_or_create(user=request.user, shopping_cart=recipe)
        if request.method == 'POST' and not created:
            raise exceptions.ValidationError(
                detail='Вы уже добавили рецепт в список покупок!'
            )
        if request.method == 'POST':
            serializer = RecipeCutSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = pagination.PageNumberPagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        subscription, created = Subscribe.objects.select_related(
            'user',
            'author'
            ).get_or_create(user=request.user, author=author)
        if request.method == 'POST' and not created:
            raise exceptions.ValidationError(
                detail='Вы уже подписались на данного автора!'
            )
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscriber__user=self.request.user)
        serializer = SubscribeSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
