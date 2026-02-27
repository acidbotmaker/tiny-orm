from pydantic import BaseModel
from typing import Optional
import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract


# Pydantic method to define the structure of Student object
class Student(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    dept: str

    # ----- create students table -----
    @staticmethod
    def create_table(conn: MySQLConnectionAbstract) -> None:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS students(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    dept CHAR(50))
                """
                )
                print("\n--- Table created successfully. ---")
            except mysql.connector.Error as error:
                print(f"Error creating table: {error}")

    # ----- add multiple records -----
    @staticmethod
    def insert_table(conn: MySQLConnectionAbstract, students: list["Student"]) -> None:
        with conn.cursor() as cursor:
            try:
                sql: str = "INSERT INTO students(name, email, dept) VALUES (%s, %s, %s)"
                val: list[tuple[str, str, str]] = [
                    (s.name, s.email, s.dept) for s in students
                ]
                cursor.executemany(sql, val)
                conn.commit()
                print(f"\n--- {cursor.rowcount} data inserted into table. ---")

            except mysql.connector.Error as error:
                print(f"Error inserting data: {error}")

    # ----- fetch and print records -----
    @staticmethod
    def read_table(conn: MySQLConnectionAbstract) -> list["Student"]:
        with conn.cursor() as cursor:
            query: str = "SELECT id, name, email, dept FROM students"
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                students: list[Student] = [
                    Student(id=row[0], name=row[1], email=row[2], dept=row[3])
                    for row in rows
                ]
                return students

            except mysql.connector.Error as error:
                print(f"Error reading table: {error}")
                return []

    # ----- finding all records -----
    @staticmethod
    def find_all(
        conn: MySQLConnectionAbstract,
        criteria: Optional[dict] = None,
        order_by: Optional[str] = "name",
        direction: str = "ASC",
        limit: Optional[int] = None,
    ) -> list["Student"]:
        with conn.cursor() as cursor:
            try:
                query = f"SELECT id, name, email, dept FROM students"
                values = []

                if criteria:
                    conditions = [f"{key} = %s" for key in criteria.keys()]
                    query += " WHERE " + " AND ".join(conditions)
                    values = list(criteria.values())

                query += f" ORDER BY {order_by} {direction} "

                if limit is not None:
                    query += f" LIMIT {limit}"

                cursor.execute(query, values)
                rows = cursor.fetchall()

                return [
                    Student(id=row[0], name=row[1], email=row[2], dept=row[3])
                    for row in rows
                ]

            except mysql.connector.Error as error:
                print(f"Error finding all data: {error}")
                return []

    # ----- finding one record -----
    @staticmethod
    def find_one(
        conn: MySQLConnectionAbstract,
        criteria: dict[str, any],
        order_by: Optional[str] = None,
        direction: str = "ASC",
    ) -> Optional["Student"]:
        with conn.cursor() as cursor:
            try:
                conditions = " AND ".join([f"{key} = %s" for key in criteria.keys()])
                values = tuple(criteria.values())

                order = f" ORDER BY {order_by} {direction} " if order_by else ""
                sql = f"SELECT id, name, email, dept FROM students WHERE {conditions} {order} LIMIT 1"

                cursor.execute(sql, values)
                row = cursor.fetchone()

                if row:
                    return Student(id=row[0], name=row[1], email=row[2], dept=row[3])
                return None

            except mysql.connector.Error as error:
                print(f"Error finding specific data: {error}")

    # ----- update the data -----
    def save(self, conn: MySQLConnectionAbstract) -> None:
        with conn.cursor() as cursor:
            try:
                if self.id:
                    sql: str = (
                        "UPDATE students SET name = %s, email = %s, dept = %s WHERE id = %s"
                    )
                    cursor.execute(sql, (self.name, self.email, self.dept, self.id))
                    action = "updated"
                else:
                    sql: str = (
                        "INSERT INTO students(name, email, dept) VALUES (%s, %s, %s)"
                    )
                    cursor.execute(sql, (self.name, self.email, self.dept))
                    self.id = cursor.lastrowid
                    action = "saved"

                conn.commit()
                print(f"--- Student {action} successfully. ---")

            except mysql.connector.Error as error:
                print(f"Error saving data: {error}")

    # ----- delete the data -----
    def delete(self, conn: MySQLConnectionAbstract) -> None:
        if not self.id:
            print("can't delete without student id")
            return

        with conn.cursor() as cursor:
            try:
                sql: str = "DELETE FROM students WHERE id = %s"
                cursor.execute(sql, (self.id,))
                conn.commit()
                print(f"\n--- {cursor.rowcount} data deleted. ---")

            except mysql.connector.Error as error:
                print(f"Error deleting data: {error}")
