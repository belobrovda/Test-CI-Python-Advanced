from __future__ import annotations
from typing import List
from sqlalchemy import ForeignKey, Integer, String, Text, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Ассоциативная таблица для связи многие-ко-многим между рецептами и ингредиентами
recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
)


class Recipe(Base):
    """Модель рецепта в базе данных"""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    cooking_time: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Время приготовления в минутах"
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    views_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество просмотров рецепта"
    )

    # Связь с ингредиентами
    ingredients: Mapped[List[Ingredient]] = relationship(
        "Ingredient", secondary=recipe_ingredient, back_populates="recipes"
    )


class Ingredient(Base):
    """Модель ингредиента в базе данных"""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )

    # Связь с рецептами
    recipes: Mapped[List[Recipe]] = relationship(
        "Recipe", secondary=recipe_ingredient, back_populates="ingredients"
    )
