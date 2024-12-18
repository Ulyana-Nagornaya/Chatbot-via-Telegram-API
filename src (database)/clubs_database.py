"""
Database structure classes.
"""
from typing import Any

import psycopg2


class Club:
    """
    Club class.
    """
    def __init__(self, name: str, info: tuple[str, str]) -> None:
        """
        Club instance initialization.

        Args:
            name (str): Name
            info (str): Info
        """
        self.name = name
        self.info = info

        self.__check_args()

    def __check_args(self) -> None:
        if not isinstance(self.name, str) or not isinstance(self.info, tuple) or \
                len(self.info) != 2 or not isinstance(self.info[0], str) \
                or not isinstance(self.info[1], str):
            raise TypeError

    def get_info(self) -> str:
        """
        Get info about club.
        """
        return f"{self.name} \n\n{self.info[1]}\n \n \n " \
               f"Подробнее о клубе можешь узнать здесь: \n{self.info[0]}"


class Category:
    """
    Club category class.
    """
    def __init__(self, name: str, clubs: list) -> None:
        """
        Category instance initialization.

        Args:
            name (str): Name
            clubs (list): Club list
        """
        self.name = name
        self.clubs = clubs

        self.__check_args()

    def __check_args(self) -> None:
        if not isinstance(self.name, str) or not isinstance(self.clubs, list):
            raise TypeError


class Database:
    """
    Database Class.
    """
    def __init__(self, db_name: str, user: str, password: str,
                 host: str, port: str) -> None:
        """
        Initialization of Database class.

        Args:
            db_name (str): Database name
            user (str): Username
            password (str): Database password
            host (str): Database host
            port (str): Database port
        """
        self.connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    def get_categories(self) -> list | Any:
        """
        Get list of categories.

        Returns:
            list: Club categories
        """
        self.cursor.execute("SELECT * FROM category")
        return self.cursor.fetchall()

    def get_clubs_by_category(self, category_id: int) -> list | Any:
        """
        Get clubs by category.

        Args:
            category_id (int): ID of category
        Returns:
            list: Clubs
        """
        self.cursor.execute("SELECT name, link, description FROM clubs WHERE category_id = %s",
                            (category_id,))
        return self.cursor.fetchall()

    def load_data(self) -> list:
        """
        Load database info.

        Returns:
            list: Club categories
        """
        categories_data = self.get_categories()
        categories = []
        for category_id, category_name in categories_data:
            clubs_info = self.get_clubs_by_category(category_id)
            clubs = [Club(name, (link, description)) for name, link, description in clubs_info]
            categories.append(Category(category_name, clubs))
        return categories

    def close(self) -> None:
        """
        Close cursor and database.
        """
        self.cursor.close()
        self.connection.close()
