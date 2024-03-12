from django_filters import rest_framework

from foodgram_backend.models import Ingredient, Recipe, Tag


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(field_name='name')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(rest_framework.FilterSet):
    """
    Фильтр.

    Позволяет искать по признакам
    is_favorited, is_in_shopping_cart.
    """

    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    is_favorited = rest_framework.filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = rest_framework.filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favoreted(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
