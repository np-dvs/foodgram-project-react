from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from foodgram_backend.models import (Favourites, Ingredient,
                                     IngredientInRecipe, Recipe, ShoppingCart,
                                     Subscribe, Tag)
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateUserSerializer, IngredientSerializer,
                          MyUserSerializer, PasswordSerializer,
                          RecipeMiniSerializer, RecipeReadSerializer,
                          RecipeSerializer, SubscribeSerializer, TagSerializer, FavoritesSerializer)


class UserVieWSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = FoodgramPagination
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        return MyUserSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            if not user.check_password(request.data.get('current_password')):
                return Response('Неверный пароль',
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(request.data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscribtions = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(subscribtions)
        serializer = SubscribeSerializer(pages, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User,
                                   id=pk)
        subscribtion = user.follower.filter(author=author)
        if request.method == 'POST':
            if subscribtion.exists():
                return Response(
                    'Нельзя подписаться на пользователя дважды',
                    status=status.HTTP_400_BAD_REQUEST)
            elif author == user:
                return Response('Подписаться на себя невозможно',
                                status=status.HTTP_400_BAD_REQUEST)
            create_subscription = Subscribe.objects.create(
                user=user, author=author
            )
            serializer = SubscribeSerializer(create_subscription)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscribtion.exists():
                return Response(
                    'Такого пользователя не существует',
                    status=status.HTTP_400_BAD_REQUEST)
            subscribtion.delete()
            return Response('Вы отписались от пользователя',
                            status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = IngredientFilter
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['patch', 'get', 'delete', 'post']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = FoodgramPagination
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeSerializer

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):

        user = self.request.user
        if request.method == 'POST':
            if not Recipe.objects.filter(id=pk).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if Favourites.objects.filter(user=user, recipe_id=pk).exists():
                return Response('Рецепт уже добавлен в избранное',
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {'user': request.user.id, 'recipe': pk}
                serializer = FavoritesSerializer(data=data,
                                         context={'request': request})
                recipe = get_object_or_404(Recipe, id=pk)
                Favourites.objects.create(user=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Recipe.objects.filter(id=pk).exists():
                return Response('Такого рецепта не существует',
                                status=status.HTTP_404_NOT_FOUND)
            obj = Favourites.objects.filter(user=user, recipe_id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response('Вы уже удалили рецепт из избранного',
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe,
                                   id=pk)
        shopping_cart = self.request.user.shopping_cart.filter(recipe=recipe)
        if request.method == 'POST':
            if shopping_cart.exists():
                return Response('Вы уже добавили рецепт в корзину',
                                status=status.HTTP_400_BAD_REQUEST)
            shopping_cart = ShoppingCart.objects.create(
                user=self.request.user, recipe=recipe
            )
            shopping_cart.save()
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        print(shopping_cart)
        if not shopping_cart.exists():
            return Response('Этого рецепта нет в корзине',
                            status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.delete()
        return Response('Рецепт удален',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.shopping_cart.exists():
            return Response('Ваша корзина пуста',
                            status=status.HTTP_400_BAD_REQUEST)
        text = 'Список ингредиентов:'
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit'
                 ).annotate(amount=Sum('amount'))
        for ingredient in ingredients:
            text += (
                f'\n{ingredient["ingredient__name"]}'
                f' ({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["amount"]}')
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    model = Recipe
    serializer_class = FavoritesSerializer

    def get_queryset(self):
        return Recipe.objects.filter(
            authot=self.request.user.pk
        )
