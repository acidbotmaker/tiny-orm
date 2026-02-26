import sys
from pathlib import Path

# parent of src/ is on the python path so all modules can be imported correctly from the classes/ sub-package
ROOT_DIR: Path = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ----- library import -----
from typing import List, Optional
from mysql.connector.connection import MySQLConnection

# ----- local import -----
from classes.Student import Student
from utils import get_db_connection


def main() -> None:
    students: List[Student] = [
        Student(name="ROHIT", email="rohit@example.com", dept="CE"),
        Student(name="VIRAT", email="virat@example.com", dept="ME"),
        Student(name="SACHIN", email="sachin@example.com", dept="IT"),
        Student(name="ABHISHEK", email="abhishek@example.com", dept="EC"),
    ]

    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        return

    # ----- create table -----
    try:
        Student.create_table(conn)

    except Exception as e:
        print(f"Error creating a table: {e}")

    # ----- insert data into table -----
    try:
        Student.insert_table(conn, students)

        print("\n-> Initial Data:")
        all_students: List[Student] = Student.read_table(conn)
        for s in all_students:
            print(f"ID: {s.id}, Name: {s.name}| Dept: {s.dept} | Email: {s.email} ")

    except Exception as e:
        print(f"Error during inserting data: {e}")

    # ----- update table data -----
    try:
        target_update = next((s for s in all_students if s.name == "ABHISHEK"), None)
        if target_update:
            # Create a new student object and keep the same ID
            updated_info = Student(
                id=target_update.id,
                name="YUVRAJ",
                email="yuvraj@example.com",
                dept="EC",
            )
            Student.update_table(conn, updated_info)

        print("\n-> Updated Data:")
        all_students: List[Student] = Student.read_table(conn)
        for s in all_students:
            print(f"ID: {s.id}, Name: {s.name}| Dept: {s.dept} | Email: {s.email} ")

    except Exception as e:
        print(f"Error updating table data: {e}")

    # ----- delete data from table -----
    try:
        target_delete = next((s for s in all_students if s.name == "SACHIN"), None)
        if target_delete:
            Student.delete_table(conn, target_delete)

        print("\n-> Final Data:")
        all_students: List[Student] = Student.read_table(conn)
        for s in all_students:
            print(f"ID: {s.id}, Name: {s.name}| Dept: {s.dept} | Email: {s.email} ")

    except Exception as e:
        print(f"Error deleting table data: {e}")

    conn.close()
    print("\n--- Connection closed successfully. ---")


if __name__ == "__main__":
    main()
