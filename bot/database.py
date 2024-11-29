import os
import mysql.connector
import time

from enum import Enum


class TableName(Enum):
    TEST = "test"


class MyDB:
    def __init__(self, retry_interval=5, keep_alive_interval=60):
        self.retry_interval = retry_interval
        self.keep_alive_interval = keep_alive_interval
        self.start_keep_alive()

    def connect(self):
        while True:
            try:
                print("Connecting to the database...")
                self.db = mysql.connector.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    database=os.getenv("DB_DATABASE"),
                )
                self.cursor = self.db.cursor(dictionary=True)
                self.init_db()
                print("Connected to the database.")
                break
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                print(f"Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)

    def start_keep_alive(self):
        """Periodically run a simple query to keep the connection alive."""
        import threading

        def keep_alive():
            while True:
                try:
                    if self.db.is_connected():
                        self.cursor.execute("SELECT 1")
                    else:
                        self.connect()
                except mysql.connector.Error as err:
                    print(f"Keep-alive error: {err}")
                    self.connect()
                time.sleep(self.keep_alive_interval)

        threading.Thread(target=keep_alive, daemon=True).start()

    def reconnect_if_needed(self):
        """Reconnect if the database connection is not available."""
        if not self.db.is_connected():
            print("Lost connection to the database. Reconnecting...")
            self.connect()

    def init_db(self):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{TableName.TEST.value}` ("
            "`test` BIGINT NOT NULL,"
            "PRIMARY KEY (`test`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

    def close(self):
        self.cursor.close()
        self.db.close()

    def insert(self, table: str, data: dict):
        """
        Insert data into the specified table.

        Args:
            table (str): The name of the table.
            data (dict): The data to insert.

        Returns:
            None
        """
        self.reconnect_if_needed()
        keys = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        print(f"INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values()))
        self.cursor.execute(
            f"INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values())
        )
        self.db.commit()

    def select(
        self,
        table: str,
        columns: list = None,
        where: dict = None,
        limit: int = None,
        order_by: str = None,
    ):
        """
        Selects data from a table in the database.

        Args:
            table (str): The name of the table.
            columns (list, optional): The columns to select. Defaults to None, which selects all columns.
            where (dict, optional): The where clause as a dictionary of column-value pairs. Defaults to None.
            limit (int, optional): The maximum number of rows to return. Defaults to None.
            order_by (str, optional): The column to order the results by. Defaults to None.

        Returns:
            tuple: The selected data as a tuple.
        """
        self.reconnect_if_needed()
        if columns is None:
            columns = ["*"]
        query = f"SELECT {', '.join(columns)} FROM `{table}`"
        if where:
            where_query = " AND ".join([f"{key} = %s" for key in where.keys()])
            query += f" WHERE {where_query}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        print(query, tuple(where.values()) if where else None)
        self.cursor.execute(query, tuple(where.values()) if where else None)
        return self.cursor.fetchall()

    def update(self, table: str, data: dict, where: dict):
        """
        Update records in the specified table based on the given conditions.

        Args:
            table (str): The name of the table to update.
            data (dict): A dictionary containing the column names as keys and the new values as values.
            where (dict): A dictionary containing the column names as keys and the conditions as values.

        Returns:
            None
        """
        self.reconnect_if_needed()
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        where_clause = " AND ".join([f"{key} = %s" for key in where.keys()])
        values = tuple(data.values()) + tuple(where.values())
        print(f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}", values)
        self.cursor.execute(
            f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}", values
        )
        self.db.commit()

    def delete(self, table: str, where: dict):
        """
        Deletes records from the specified table based on the given WHERE clause.

        Args:
            table (str): The name of the table to delete records from.
            where (dict): A dictionary containing the column names as keys and the values as the conditions for deletion.

        Returns:
            None
        """
        self.reconnect_if_needed()
        where_clause = " AND ".join([f"{key} = %s" for key in where.keys()])
        print(f"DELETE FROM `{table}` WHERE {where_clause}", tuple(where.values()))
        self.cursor.execute(
            f"DELETE FROM `{table}` WHERE {where_clause}", tuple(where.values())
        )
        self.db.commit()


db = MyDB(
    retry_interval=10, keep_alive_interval=60
)  # Retry connection every 10 seconds, keep-alive every 60 seconds
