from django.contrib import admin
from django.contrib.admin import display

from .models import (Favourites, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Subscribe, Tag)


@admin.register(Recipe)
class AdminRecipe(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_to_favorites',)
    readonly_fields = ('added_to_favorites',)
    list_filter = ('author', 'name', 'tags')

    @display(description='В избранном')
    def added_to_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class AdminIngredient(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(IngredientInRecipe)
class AdminIngredientInRecipe(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(Favourites)
class AdminFavorites(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class AdminShoppingCart(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Subscribe)
class AdminSubscribe(admin.ModelAdmin):
    list_display = ('user', 'author')
