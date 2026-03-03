from pydantic import BaseModel
import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract
from typing import Optional, Union, Any


class DbModel(BaseModel):
    id: Optional[int] = None

    # === Saving all records into the table ===
    def save(self, conn: MySQLConnectionAbstract) -> None:
        is_student = isinstance(self, Student)
        table_name = "students" if is_student else "teachers"
        param = "dept" if is_student else "sub"
        param_value = getattr(self, param)

        with conn.cursor() as cursor:
            try:
                if self.id:
                    query = f"UPDATE {table_name} SET name = %s, email = %s, {param} = %s WHERE id = %s"
                    cursor.execute(query, (self.name, self.email, param_value, self.id))
                else:
                    query = f"INSERT INTO {table_name}(name, email, {param}) VALUES (%s, %s, %s)"
                    cursor.execute(query, (self.name, self.email, param_value))
                    self.id = cursor.lastrowid
                    action = "saved"
                    print(f"--- {table_name} {action} successfully ---")
                conn.commit()
            except mysql.connector.Error as error:
                print(f"Error saving records: {error}")

    # === Deleting records from the table ===
    def delete(self, conn: MySQLConnectionAbstract) -> None:
        table_name = "students" if isinstance(self, Student) else "teachers"

        if not self.id:
            print(f"can't delete {table_name} without an id.")
            return

        with conn.cursor() as cursor:
            try:
                query = f"DELETE FROM {table_name} WHERE id = %s"
                cursor.execute(query, (self.id,))
                conn.commit()
                print(f"\n-> {cursor.rowcount} record deleting...")
            except mysql.connector.Error as error:
                conn.rollback()
                print(f"Error deleting record: {error}")


class Teacher(DbModel):
    name: str
    email: str
    sub: str


class Student(DbModel):
    name: str
    email: str
    dept: str


class SchoolDb(BaseModel):

    # === create table ===
    @staticmethod
    def create_table(conn: MySQLConnectionAbstract) -> None:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS teachers(
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255),
                        email VARCHAR(255),
                        sub CHAR(50)
                    )
                """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS students(
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255),
                        email VARCHAR(255),
                        dept CHAR(50)
                    )
                """
                )
                print("=== Tables created successfully ===")
            except mysql.connector.Error as error:
                print(f"Error creating table: {error}")

    #  === Inserting records into table ===
    @staticmethod
    def insert_data(
        conn: MySQLConnectionAbstract,
        students: Optional[list["Student"]] = None,
        teachers: Optional[list["Teacher"]] = None,
    ) -> None:
        with conn.cursor() as cursor:
            try:
                if students:
                    query: str = (
                        "INSERT INTO students(name, email, dept) VALUES (%s, %s, %s)"
                    )
                    values = [(s.name, s.email, s.dept) for s in students]
                    cursor.executemany(query, values)

                if teachers:
                    query: str = (
                        "INSERT INTO teachers(name, email, sub) VALUES (%s, %s, %s)"
                    )
                    values = [(t.name, t.email, t.sub) for t in teachers]
                    cursor.executemany(query, values)

                conn.commit()
                print(f"=== {cursor.rowcount} records inserted successfully ===")
            except mysql.connector.Error as error:
                print(f"Error inserting data into table: {error}")
                conn.rollback()

    # === Finding all data according to the table_name ===
    @staticmethod
    def find_all(
        conn: MySQLConnectionAbstract,
        model_class: Union[type[Student], type[Teacher]],
        criteria: Optional[dict] = None,
        order_by: str = "name",
        direction: str = "ASC",
        limit: Optional[int] = None,
    ) -> list[Any]:
        is_student = model_class == Student
        table_name = "students" if is_student else "teachers"
        param = "dept" if is_student else "sub"

        allowed_columns = {"id", "name", "email", param}
        updated_order_by = order_by if order_by in allowed_columns else "name"
        updated_direction = (
            direction.upper() if direction.upper() in {"ASC", "DESC"} else "ASC"
        )

        query = f"SELECT id, name, email, {param} FROM {table_name}"
        values = []

        if criteria:
            valid_criteria = {k: v for k, v in criteria.items() if k in allowed_columns}
            if valid_criteria:
                conditions = [f"{key} = %s" for key in valid_criteria.keys()]
                query += " WHERE " + " AND ".join(conditions)
                values = list(valid_criteria.values())

        query += f" ORDER BY {updated_order_by} {updated_direction}"

        if isinstance(limit, int):
            query += f" Limit {limit}"

        with conn.cursor() as cursor:
            try:
                cursor.execute(query, values)
                rows = cursor.fetchall()

                return [
                    model_class(id=row[0], name=row[1], email=row[2], **{param: row[3]})
                    for row in rows
                ]
            except mysql.connector.Error as error:
                print(f"Error finding all data: {error}")
                return []

    # === Finding specific value according to the table_name ===
    @staticmethod
    def find_one(
        conn: MySQLConnectionAbstract,
        model_split: Union[type[Student], type[Teacher]],
        criteria: dict,
        order_by: Optional[str] = "name",
        direction: str = "ASC",
    ) -> Optional[Any]:
        try:
            results = SchoolDb.find_all(
                conn, model_split, criteria, order_by, direction, limit=1
            )
            return results[0] if results else None
        except mysql.connector.Error as error:
            print(f"Error finding one record: {error}")
            return None
