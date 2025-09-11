from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class IngredientBase(BaseModel):
    """Базовая схема ингредиента"""
    name: str = Field(..., max_length=100, description="Название ингредиента")


class IngredientCreate(IngredientBase):
    """Схема для создания ингредиента"""
    pass


class IngredientResponse(IngredientBase):
    """Схема ответа с информацией об ингредиенте"""
    id: int
    
    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    """Базовая схема рецепта"""
    title: str = Field(..., max_length=200, description="Название блюда")
    cooking_time: int = Field(..., gt=0, description="Время приготовления в минутах")
    description: str = Field(..., description="Текстовое описание рецепта")


class RecipeCreate(RecipeBase):
    """Схема для создания рецепта"""
    ingredient_ids: List[int] = Field(..., description="Список ID ингредиентов")


class RecipeResponse(RecipeBase):
    """Схема ответа с информацией о рецепте"""
    id: int
    views_count: int
    ingredients: List[IngredientResponse]
    
    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    """Схема ответа для списка рецептов"""
    id: int
    title: str
    cooking_time: int
    views_count: int
    
    class Config:
        from_attributes = True
