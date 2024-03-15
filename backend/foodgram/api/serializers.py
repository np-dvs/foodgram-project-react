from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from foodgram_backend.models import (Ingredient, IngredientInRecipe, Recipe,
                                     Subscribe, Tag, Favourites)

User = get_user_model()


class MyUserSerializer(UserSerializer):
    """Сериализатор для модели Юзер."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and (user.follower
                                      .filter(author=obj.id).exists()):
            return True
        return False


class CreateUserSerializer(UserSerializer):
    """Сериализатор для создания юзера."""

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if 'last_name' not in validated_data:
            raise ValidationError('Укажите параметр "last_name"')
        user = User(email=validated_data['email'],
                    username=validated_data['username'],
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class PasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для смены пароля."""

    current_password = serializers.CharField(required=True,
                                             write_only=True)
    new_password = serializers.CharField(required=True,
                                         write_only=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def validate_new_password(self, value):
        validate_password(value)
        return value


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """
    Вспомогательный.

    Сериализатор для отображения рецептов
    в подписках.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')
        read_only_fields = ('id', 'name',
                            'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError(
                'Подписаться на себя невозможно'
            )
        return data

    def get_is_subscribed(self, obj):
        if obj.user.follower.filter(author=obj.author).exists():
            return True
        return False

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeMiniSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов в рецепте."""

    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте (создание)."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient
                                            .objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True,
                                               source='ingredient_in_recipe')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()

    # def get_ingredients(self, obj):
    #     recipe = obj
    #     ingredients = recipe.ingredients.values(
    #         'id',
    #         'name',
    #         'measurement_unit'
    #     )
    #     print(recipe)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для POST и PATCH запросов рецепта."""

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientRecipeCreateSerializer(many=True)
    author = MyUserSerializer(read_only=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate_image(self, value):
        image = value
        if not image:
            raise ValidationError('Добавьте фото вашего шедевра')
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError('Вы не добавили ингредиенты')
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise ValidationError('Вы уже добавили этот ингредиент')
            if int(ingredient['amount']) < 1:
                raise ValidationError('Слишком мало! Добавьте хотя бы 1')
            ingredients_list.append(ingredient['id'])
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError('Теги не добавлены - тегните что-нибудь')
        tag_list = []
        for i in tags:
            if i in tag_list:
                raise ValidationError('Такой тег уже добавлен')
            tag_list.append(i)
        return value

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' not in validated_data:
            raise ValidationError('Укажите хотя бы один тег')
        if 'ingredients' not in validated_data:
            raise ValidationError('Укажите хотя бы один ингредиент')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for ingredient in ingredients:
            object = IngredientInRecipe.objects.get(
                recipe=instance,
                ingredient=ingredient['id'])
            object.amount = ingredient['amount']
            object.save()
        instance.tags.clear()
        instance.tags.set(tags)
        instance.save()
        return super().update(instance,
                              validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context={'request':
                                             self.context['request']}).data


class RecipeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'

    def to_representation(self, instance):
        return RecipeMiniSerializer(
            instance=instance.recipe,
            context=self.context
        ).data
