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
from .serializers import (CreateFavoriteSerializer,
                          CreateShoppingCartSerializer,
                          CreateSubscribeSerializer, CreateUserSerializer,
                          IngredientSerializer, PasswordSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          SubscribeSerializer, TagSerializer, UserSerializer)


class UserVieWSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = FoodgramPagination
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        return UserSerializer

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

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        context = {'request': request}
        subscribtion = get_object_or_404(User, id=pk)
        data = {
            'user': subscribtion.id,
            'author': request.user.id
        }
        serializer = CreateSubscribeSerializer(data=data,
                                               context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def destroy_subscribe(self, request, pk):
        subscription = Subscribe.objects.filter(
            user_id=get_object_or_404(User, id=pk),
            author=request.user.id
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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

    def delete_favorite(self, request, pk, model):
        model = model.objects.filter(
            author=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        )
        if model.exists():
            model.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = CreateFavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_destroy(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        Favourites.objects.get(user=request.user,
                               recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = CreateShoppingCartSerializer(data=data,
                                                  context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        ShoppingCart.objects.filter(
            user=request.user.id,
            recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
