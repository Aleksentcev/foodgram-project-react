from rest_framework import status, viewsets, permissions, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, Subscribe
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    IngredientRecipe,
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    RecipeCutSerializer,
    CustomUserSerializer,
    SubscribeSerializer
)
from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient',
            'tags',
            'author'
        ).all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    def add_remove_recipe(self, request, id, model):
        recipe = get_object_or_404(Recipe, id=id)
        obj, created = model.objects.select_related(
            'user', 'recipe'
        ).get_or_create(user=request.user, recipe=recipe)
        if request.method == 'POST' and created:
            serializer = RecipeCutSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE' and obj:
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise exceptions.ValidationError(
            detail='Вы уже совершили это действие!'
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        return self.add_remove_recipe(
            request,
            self.kwargs.get('pk'),
            Favorite
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, **kwargs):
        return self.add_remove_recipe(
            request,
            self.kwargs.get('pk'),
            ShoppingCart
        )

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount=Sum('amount')))
        pretty_ings = []
        for ingredient in ingredients:
            pretty_ings.append('{name} - {amount} {m_unit}\n'.format(
                name=ingredient.get('ingredient__name'),
                amount=ingredient.get('amount'),
                m_unit=ingredient.get('ingredient__measurement_unit')
            ))
        response = FileResponse(pretty_ings, content_type='text/plain')
        return response


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
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        subscription, created = Subscribe.objects.get_or_create(
            user=request.user,
            author=author
        )
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
