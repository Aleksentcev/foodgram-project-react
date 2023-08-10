from django.contrib import admin

from .models import Ingredient, Tag, Recipe, IngredientRecipe, TagRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'tags',
        'count_favorite'
    )
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientRecipeInLine, TagRecipeInLine)

    def count_favorite(self, obj):
        return obj.favorites.count()
