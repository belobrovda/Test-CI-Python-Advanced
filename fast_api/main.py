from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List
from contextlib import asynccontextmanager

from starlette.responses import JSONResponse

from fast_api.database import get_db, create_tables
from fast_api.models import Recipe, Ingredient
from fast_api.schemas import (
    RecipeCreate,
    RecipeResponse,
    RecipeListResponse,
    IngredientResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="CookBook API",
    description="API для кулинарной книги с рецептами",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@cookbook.com",
    },
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Корневой endpoint для проверки работы API"""
    return {
        "message": "Добро пожаловать в CookBook API!",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get(
    "/recipes",
    response_model=List[RecipeListResponse],
    summary="Получить список всех рецептов",
    description="""Возвращает список всех рецептов, отсортированных по популярности.

    **Сортировка:**
    - По убыванию количества просмотров (популярности)
    - При равном количестве просмотров - по возрастанию времени приготовления

    **Используется для:** Первого экрана приложения - таблицы со списком рецептов.
    """,
)
async def get_recipes(db: Session = Depends(get_db)):
    """
    Получает список всех рецептов с сортировкой:
    1. По количеству просмотров (по убыванию)
    2. По времени приготовления (по возрастанию) при равных просмотрах
    """
    recipes = (
        db.query(Recipe)
        .order_by(desc(Recipe.views_count), asc(Recipe.cooking_time))
        .all()
    )

    return recipes


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse,
    summary="Получить детальную информацию о рецепте",
    description="""Возвращает полную информацию о конкретном рецепте по его ID.

    **Включает:**
    - Название блюда
    - Время приготовления
    - Список ингредиентов
    - Текстовое описание
    - Количество просмотров

    **Примечание:** При каждом успешном запросе увеличивает счетчик просмотров на 1.

    **Используется для:** Второго экрана приложения - детальной информации о рецепте.
    """,
)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """
    Получает детальную информацию о рецепте по ID и увеличивает счетчик просмотров.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рецепт с ID {recipe_id} не найден",
        )

    # Увеличиваем счетчик просмотров
    recipe.views_count += 1
    db.commit()
    db.refresh(recipe)

    return recipe


@app.post(
    "/recipes",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="""Создает новый рецепт в кулинарной книге.

    **Требуемые поля:**
    - title: Название блюда (макс. 200 символов)
    - cooking_time: Время приготовления в минутах (должно быть > 0)
    - description: Текстовое описание рецепта
    - ingredient_ids: Список ID существующих ингредиентов

    **Примечание:** Ингредиенты должны быть созданы заранее.

    **Возвращает:** Созданный рецепт со всей информацией.
    """,
)
async def create_recipe(recipe_data: RecipeCreate, db: Session = Depends(get_db)):
    """
    Создает новый рецепт с указанными ингредиентами.
    """
    # Проверяем существование всех ингредиентов
    ingredients = []
    for ingredient_id in recipe_data.ingredient_ids:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ингредиент с ID {ingredient_id} не найден",
            )
        ingredients.append(ingredient)

    # Создаем новый рецепт
    new_recipe = Recipe(
        title=recipe_data.title,
        cooking_time=recipe_data.cooking_time,
        description=recipe_data.description,
        ingredients=ingredients,
    )

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    return new_recipe


@app.get(
    "/ingredients",
    response_model=List[IngredientResponse],
    summary="Получить список всех ингредиентов",
    description="Возвращает список всех доступных ингредиентов в системе.",
)
async def get_ingredients(db: Session = Depends(get_db)):
    """Получает список всех ингредиентов"""
    return db.query(Ingredient).all()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
