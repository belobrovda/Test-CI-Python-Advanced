from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Ассоциативная таблица для связи многие-ко-многим между рецептами и ингредиентами
recipe_ingredient = Table(
    'recipe_ingredient',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'))
)


class Recipe(Base):
    """Модель рецепта в базе данных"""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    cooking_time = Column(Integer, nullable=False, comment="Время приготовления в минутах")
    description = Column(Text, nullable=False)
    views_count = Column(Integer, default=0, comment="Количество просмотров рецепта")

    # Связь с ингредиентами
    ingredients = relationship("Ingredient", secondary=recipe_ingredient, back_populates="recipes")


class Ingredient(Base):
    """Модель ингредиента в базе данных"""
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    
    # Связь с рецептами
    recipes = relationship("Recipe", secondary=recipe_ingredient, back_populates="ingredients")