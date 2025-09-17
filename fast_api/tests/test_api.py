import unittest

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fast_api.database import get_db
from fast_api.main import app
from fast_api.models import Base, Ingredient, Recipe


class TestCookbookAPI(unittest.TestCase):
    """Тесты для API кулинарной книги"""

    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        # Настройка тестовой базы данных в памяти
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )

        # Создаем таблицы
        Base.metadata.create_all(bind=cls.engine)

        # Наполняем тестовыми данными
        cls.populate_test_data()

    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        Base.metadata.drop_all(bind=cls.engine)

    @classmethod
    def populate_test_data(cls):
        """Наполнение базы тестовыми данными"""
        db = cls.TestingSessionLocal()
        try:
            # Создаем ингредиенты
            ingredients = [
                Ingredient(name="Спагетти"),
                Ingredient(name="Бекон"),
                Ingredient(name="Яйца"),
                Ingredient(name="Сыр Пармезан"),
                Ingredient(name="Мука"),
                Ingredient(name="Сахар"),
            ]

            for ingredient in ingredients:
                db.add(ingredient)
            db.commit()

            # Создаем рецепты
            recipe1 = Recipe(
                title="Спагетти Карбонара",
                cooking_time=20,
                description="Классический итальянский рецепт",
                views_count=5,
                ingredients=ingredients[:4],  # Первые 4 ингредиента
            )

            recipe2 = Recipe(
                title="Яблочный пирог",
                cooking_time=45,
                description="Вкусный домашний пирог",
                views_count=3,
                ingredients=ingredients[4:],  # Последние 2 ингредиента
            )

            db.add_all([recipe1, recipe2])
            db.commit()

        finally:
            db.close()

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db = self.TestingSessionLocal()

        # Переопределяем зависимость базы данных
        def override_get_db():
            try:
                yield self.db
            finally:
                self.db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальную зависимость
        app.dependency_overrides.clear()
        self.db.close()

    def test_root_endpoint(self):
        """Тест корневого endpoint"""
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Добро пожаловать", response.json()["message"])
        print("✅ Корневой endpoint работает корректно")

    def test_get_recipes(self):
        """Тест получения списка рецептов"""
        response = self.client.get("/recipes")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Должно быть 2 рецепта
        self.assertEqual(len(data), 3)

        # Проверяем сортировку (по убыванию просмотров)
        self.assertGreaterEqual(data[0]["views_count"], data[1]["views_count"])

        # Проверяем структуру данных
        for recipe in data:
            self.assertIn("id", recipe)
            self.assertIn("title", recipe)
            self.assertIn("cooking_time", recipe)
            self.assertIn("views_count", recipe)

        print("✅ Получение списка рецептов работает корректно")

    def test_get_recipe_detail(self):
        """Тест получения детальной информации о рецепте"""
        # Сначала получаем список рецептов чтобы узнать ID
        recipes_response = self.client.get("/recipes")
        recipe_id = recipes_response.json()[0]["id"]
        initial_views = recipes_response.json()[0]["views_count"]

        # Получаем детальную информацию
        response = self.client.get(f"/recipes/{recipe_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Проверяем структуру данных
        self.assertEqual(data["id"], recipe_id)
        self.assertIn("ingredients", data)
        self.assertIn("description", data)

        # Проверяем что счетчик просмотров увеличился
        self.assertEqual(data["views_count"], initial_views + 1)

        print("✅ Детальная информация о рецепте работает корректно")

    def test_get_nonexistent_recipe(self):
        """Тест получения несуществующего рецепта"""
        response = self.client.get("/recipes/9999")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("не найден", response.json()["detail"])

        print("✅ Обработка несуществующего рецепта работает корректно")

    def test_get_ingredients(self):
        """Тест получения списка ингредиентов"""
        response = self.client.get("/ingredients")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Должно быть минимум 6 ингредиентов
        self.assertGreaterEqual(len(data), 6)

        # Проверяем структуру данных
        for ingredient in data:
            self.assertIn("id", ingredient)
            self.assertIn("name", ingredient)

        print("✅ Получение списка ингредиентов работает корректно")

    def test_create_recipe_with_nonexistent_ingredients(self):
        """Тест создания рецепта с несуществующими ингредиентами"""
        recipe_data = {
            "title": "Рецепт с несуществующими ингредиентами",
            "cooking_time": 30,
            "description": "Описание",
            "ingredient_ids": [999, 1000],  # Несуществующие ID
        }

        response = self.client.post("/recipes", json=recipe_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("не найден", response.json()["detail"])

        print("✅ Обработка несуществующих ингредиентов работает корректно")

    def test_create_recipe(self):
        """Тест создания нового рецепта"""
        recipe_data = {
            "title": "Тестовый рецепт",
            "cooking_time": 30,
            "description": "Тестовое описание рецепта",
            "ingredient_ids": [1, 2, 3],  # Существующие ID ингредиентов
        }

        response = self.client.post("/recipes", json=recipe_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()

        self.assertEqual(data["title"], recipe_data["title"])
        self.assertEqual(data["cooking_time"], recipe_data["cooking_time"])
        self.assertEqual(data["views_count"], 0)  # Новый рецепт без просмотров
        self.assertEqual(len(data["ingredients"]), 3)  # 3 ингредиента

        print("✅ Создание рецепта работает корректно")
