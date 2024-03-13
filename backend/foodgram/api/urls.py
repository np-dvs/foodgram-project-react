from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserVieWSet

app_name = 'api'

router = DefaultRouter()

router.register(r'users', UserVieWSet, basename='users_api')
router.register(r'recipes', RecipeViewSet, basename='recipe_api')
router.register(r'tags', TagViewSet, basename='tags_api')
router.register(r'ingredients', IngredientViewSet, basename='ingredients_api')
# router.register(r'favorites', FavoritesViewSet, basename='favorites_api')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
