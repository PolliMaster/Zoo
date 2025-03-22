import flet as ft
import sqlite3

def get_tables():
    conn = sqlite3.connect("instance\data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def load_data(table_name):
    conn = sqlite3.connect("instance\data.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]  # Получаем названия столбцов
    conn.close()
    return columns, rows

def main(page: ft.Page):
    page.title = "БД"
    page.scroll = "adaptive"
    
    tables = get_tables()
    dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(table) for table in tables],
        on_change=lambda e: update_table(e.control.value, page, dropdown),
        expand=True
    )
    
    container = ft.Column([dropdown], expand=True)
    page.add(container)

def update_table(table_name, page, dropdown):
    columns, rows = load_data(table_name)
    table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(col)) for col in columns],
        rows=[
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]
            ) for row in rows
        ],
        expand=True
    )
    page.controls.clear()
    page.add(ft.Column([dropdown, table], expand=True))
    page.update()

ft.app(target=main)