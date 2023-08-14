from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientRecipe,
    TagRecipe,
    Favorite,
    ShoppingCart
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


class IngredientRecipeForm(BaseInlineFormSet):

    def clean(self):
        super(IngredientRecipeForm, self).clean()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            if data.get('DELETE'):
                raise ValidationError(
                    'Нельзя удалять все ингредиенты из рецепта даже в админке!'
                )


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    formset = IngredientRecipeForm


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )


class TagRecipeForm(BaseInlineFormSet):

    def clean(self):
        super(TagRecipeForm, self).clean()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            if data.get('DELETE'):
                raise ValidationError(
                    'Нельзя удалять все теги из рецепта даже в админке!'
                )


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    min_num = 1
    formset = TagRecipeForm


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'count_favorite'
    )
    list_filter = ('author', 'tags')
    search_fields = ('name',)
    inlines = (IngredientRecipeInLine, TagRecipeInLine)

    def count_favorite(self, obj):
        return obj.favorites.count()


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
