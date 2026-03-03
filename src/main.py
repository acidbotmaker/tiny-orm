import sys
from pathlib import Path

# parent of src/ is on the python path so all modules can be imported correctly from the classes/ sub-package
ROOT_DIR: Path = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ----- library import -----
from typing import List, Optional, Union, Type
from mysql.connector.connection import MySQLConnection

# ----- local import -----
from classes.SchoolDb import SchoolDb, Student, Teacher
from utils import get_db_connection


def _print_record(record: Union[Student, Teacher]) -> None:
    if isinstance(record, Student):
        print(
            f"ID: {record.id} | Name: {record.name} | Email: {record.email} | Dept: {record.dept}"
        )
    else:
        print(
            f"ID: {record.id} | Name: {record.name} | Email: {record.email} | Sub: {record.sub}"
        )


def crud_operations(
    conn: MySQLConnection,
    model: Type[Union[Student, Teacher]],
    table_name: List[Union[Student, Teacher]],
    update_target_name: str,
    update_fields: dict,
    delete_target_name: str,
    find_one_criteria: dict,
    find_all_criteria: dict,
) -> None:
    label = model.__name__

    # ----- create/insert table -----
    print(f"\n--- Initializing {label} records ---")
    for record in table_name:
        record.save(conn)

    # ----- finding all records from table -----
    all_records = SchoolDb.find_all(conn, model)
    print(f"\nTotal {label}s: {len(all_records)}")

    # ----- Filter by department -----
    print(f"\n-> Searching one {label} with criteria {find_one_criteria}:")
    single_record = SchoolDb.find_one(conn, model, criteria=find_one_criteria)
    if single_record:
        _print_record(single_record)
    else:
        print(f"No {label}s found matching the criteria.")

    # ----- Filter by multiple criteria -----
    print(f"\n-> Searching all {label}s with criteria {find_all_criteria}:")
    filter_results = SchoolDb.find_all(conn, model, criteria=find_all_criteria)
    if filter_results:
        for f in filter_results:
            _print_record(f)
    else:
        print(f"No {label}s found matching the criteria.")

    # ----- update table record -----
    current_data = SchoolDb.find_all(conn, model)
    target_record = next(
        (r for r in current_data if r.name == update_target_name), None
    )
    if target_record:
        print(f"\n-> Updating {update_target_name} to {update_fields.get('name')}...")
        for field, value in update_fields.items():
            setattr(target_record, field, value)
        target_record.save(conn)
        print(
            f"Updated: {model.__name__}s table record from {update_target_name} to {target_record.name} successfully."
        )

    # ----- delete record from table -----
    current_data = SchoolDb.find_all(conn, model)
    target_delete = next(
        (r for r in current_data if r.name == delete_target_name), None
    )
    if target_delete:
        target_delete.delete(conn)
        print(f"Deleted: {delete_target_name} from the {model.__name__}s table.")

    print("\n-> Final Data:")
    final_records = SchoolDb.find_all(conn, model)
    for r in final_records:
        _print_record(r)

    # ----- finding all record from table after CRUD operations -----
    print(f"\nTotal {model.__name__}s after CRUD operation: {len(final_records)}\n")


def main() -> None:
    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        print("Failed to connect to the database.")
        return

    try:
        # ----- create table -----
        SchoolDb.create_table(conn)

        print("\n===== STUDENT OPERATIONS =====")

        # ----- insert record into students table -----
        students: List[Student] = [
            Student(name="ROHIT", email="rohit@example.com", dept="CE"),
            Student(name="VIRAT", email="virat@example.com", dept="ME"),
            Student(name="SACHIN", email="sachin@example.com", dept="IT"),
            Student(name="ABHISHEK", email="abhishek@example.com", dept="EC"),
        ]

        crud_operations(
            conn=conn,
            model=Student,
            table_name=students,
            update_target_name="ABHISHEK",
            update_fields={
                "name": "YUVRAJ",
                "email": "yuvraj@example.com",
                "dept": "AIML",
            },
            delete_target_name="SACHIN",
            find_one_criteria={"dept": "EC"},
            find_all_criteria={"name": "ROHIT", "dept": "CE"},
        )

        print("===== TEACHER OPERATIONS =====")

        # ----- insert record into teachers table -----
        teachers: List[Teacher] = [
            Teacher(name="John", email="john@example.com", sub="DSA"),
            Teacher(name="Alice", email="alice@example.com", sub="Python"),
            Teacher(name="David", email="david@example.com", sub="DBMS"),
            Teacher(name="Willson", email="willson@example.com", sub="Maths"),
        ]

        crud_operations(
            conn=conn,
            model=Teacher,
            table_name=teachers,
            update_target_name="Willson",
            update_fields={"name": "Steve", "email": "steve@example.com", "sub": "ML"},
            delete_target_name="David",
            find_one_criteria={"sub": "Maths"},
            find_all_criteria={"name": "Alice", "sub": "Python"},
        )

    except Exception as e:
        print(f"Error during execution: {e}")

    finally:
        conn.close()
        print("--- Connection closed successfully. ---")


if __name__ == "__main__":
    main()
