from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fast_api.models import Base, Recipe, Ingredient

# Настройка подключения к базе данных (SQLite для примера)
SQLALCHEMY_DATABASE_URL = "sqlite:///./cookbook.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Зависимость для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Создание таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)


def populate_test_data():
    """Наполняет базу данных тремя тестовыми рецептами с ингредиентами"""
    db = SessionLocal()

    try:
        # Проверяем, есть ли уже данные в базе
        existing_recipes = db.query(Recipe).count()
        if existing_recipes > 0:
            print("База данных уже содержит рецепты. Пропускаем наполнение.")
            return

        # Создаем ингредиенты
        ingredients_data = [
            "Спагетти", "Бекон", "Яйца", "Сыр Пармезан", "Чеснок", "Сливки",
            "Мука", "Сахар", "Яблоки", "Корица", "Сливочное масло", "Яйцо",
            "Куриное филе", "Лук", "Морковь", "Рис", "Соевый соус", "Имбирь",
            "Растительное масло", "Зеленый лук", "Кунжут"
        ]

        ingredients = []
        for name in ingredients_data:
            ingredient = Ingredient(name=name)
            db.add(ingredient)
            ingredients.append(ingredient)

        db.commit()

        # Рецепт 1: Спагетти Карбонара
        carbonara_ingredients = [
            ingredients[0],  # Спагетти
            ingredients[1],  # Бекон
            ingredients[2],  # Яйца
            ingredients[3],  # Сыр Пармезан
            ingredients[4]  # Чеснок
        ]

        carbonara = Recipe(
            title="Спагетти Карбонара",
            cooking_time=20,
            description="""Классический итальянский рецепт пасты карбонара.

            Шаги приготовления:
            1. Отварите спагетти согласно инструкции на упаковке
            2. Обжарьте бекон с чесноком до хрустящей корочки
            3. Взбейте яйца с тертым пармезаном
            4. Смешайте горячие спагетти с яичной смесью и беконом
            5. Подавайте сразу же, украсив дополнительным сыром""",
            ingredients=carbonara_ingredients
        )

        # Рецепт 2: Яблочный пирог
        apple_pie_ingredients = [
            ingredients[6],  # Мука
            ingredients[7],  # Сахар
            ingredients[8],  # Яблоки
            ingredients[9],  # Корица
            ingredients[10],  # Сливочное масло
            ingredients[11]  # Яйцо
        ]

        apple_pie = Recipe(
            title="Яблочный пирог",
            cooking_time=45,
            description="""Вкусный домашний яблочный пирог с корицей.

            Шаги приготовления:
            1. Приготовьте тесто из муки, масла, сахара и яйца
            2. Нарежьте яблоки тонкими дольками
            3. Смешайте яблоки с корицей и сахаром
            4. Выложите начинку на тесто
            5. Выпекайте при 180°C 35-40 минут до золотистой корочки""",
            ingredients=apple_pie_ingredients
        )

        # Рецепт 3: Курица с рисом по-азиатски
        chicken_rice_ingredients = [
            ingredients[12],  # Куриное филе
            ingredients[13],  # Лук
            ingredients[14],  # Морковь
            ingredients[15],  # Рис
            ingredients[16],  # Соевый соус
            ingredients[17],  # Имбирь
            ingredients[18],  # Растительное масло
            ingredients[19],  # Зеленый лук
            ingredients[20]  # Кунжут
        ]

        chicken_rice = Recipe(
            title="Курица с рисом по-азиатски",
            cooking_time=30,
            description="""Ароматное азиатское блюдо с курицей и рисом.

            Шаги приготовления:
            1. Обжарьте курицу с луком и морковью
            2. Добавьте натертый имбирь и готовьте 2 минуты
            3. Влейте соевый соус и добавьте отварной рис
            4. Тщательно перемешайте и прогрейте
            5. Подавайте, украсив зеленым луком и кунжутом""",
            ingredients=chicken_rice_ingredients
        )

        # Добавляем рецепты в базу
        db.add_all([carbonara, apple_pie, chicken_rice])
        db.commit()

        print("База данных успешно наполнена 3 рецептами!")
        print("1. Спагетти Карбонара")
        print("2. Яблочный пирог")
        print("3. Курица с рисом по-азиатски")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при наполнении базы данных: {e}")
    finally:
        db.close()
