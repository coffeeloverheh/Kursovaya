import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


# Создание базы данных
def initialize_database():
    conn = sqlite3.connect('cinema.db')
    c = conn.cursor()

    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL)''')

    # Таблица фильмов
    c.execute('''CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    description TEXT,
                    schedule TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'доступен')''')

    # Таблица статистики
    c.execute('''CREATE TABLE IF NOT EXISTS statistics (
                    movie_id INTEGER,
                    user_id INTEGER,
                    review TEXT,
                    FOREIGN KEY (movie_id) REFERENCES movies (id),
                    FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Создание аккаунтов администратора и сотрудника (при первом запуске)
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('admin', 'admin', 'admin'))
    c.execute("SELECT * FROM users WHERE role='employee'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('employee', 'employee', 'employee'))

    conn.commit()
    conn.close()


# Функция регистрации
def register_user():
    username = entry_username.get()
    password = entry_password.get()

    if username and password:
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует")
        else:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, password, 'user'))
            conn.commit()
            messagebox.showinfo("Успех", "Регистрация завершена")
        conn.close()
    else:
        messagebox.showerror("Ошибка", "Заполните все поля")


# Функция авторизации
def login_user():
    username = entry_username.get()
    password = entry_password.get()

    if username and password:
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            role = user[3]
            if role == 'user':
                user_interface()
            elif role == 'admin':
                admin_interface()
            elif role == 'employee':
                employee_interface()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")
    else:
        messagebox.showerror("Ошибка", "Заполните все поля")


# Интерфейс пользователя
def user_interface():
    def show_movies():
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT title, genre, description, schedule, status FROM movies WHERE status='доступен'")
        movies = c.fetchall()
        conn.close()

        tree_movies.delete(*tree_movies.get_children())
        for movie in movies:
            tree_movies.insert('', 'end', values=movie)

    user_window = tk.Toplevel()
    user_window.title("Афиша кинотеатра")

    tk.Label(user_window, text="Список фильмов:").pack()
    tree_movies = ttk.Treeview(user_window, columns=("Название", "Жанр", "Описание", "Расписание", "Статус"),
                               show='headings')
    for col in tree_movies["columns"]:
        tree_movies.heading(col, text=col)
    tree_movies.pack()

    tk.Button(user_window, text="Обновить афишу", command=show_movies).pack()

    show_movies()


# Интерфейс администратора
def admin_interface():
    def add_movie():
        title = entry_title.get()
        genre = entry_genre.get()
        description = entry_description.get()
        schedule = entry_schedule.get()

        if title and genre and schedule:
            conn = sqlite3.connect('cinema.db')
            c = conn.cursor()
            c.execute("INSERT INTO movies (title, genre, description, schedule) VALUES (?, ?, ?, ?)",
                      (title, genre, description, schedule))
            conn.commit()
            conn.close()
            refresh_movies()
            messagebox.showinfo("Успех", "Фильм добавлен в афишу")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля")

    def edit_movie():
        selected_item = tree_movies.selection()
        if selected_item:
            movie_id = tree_movies.item(selected_item)['values'][0]
            title = entry_title.get()
            genre = entry_genre.get()
            description = entry_description.get()
            schedule = entry_schedule.get()

            if title and genre and schedule:
                conn = sqlite3.connect('cinema.db')
                c = conn.cursor()
                c.execute("UPDATE movies SET title=?, genre=?, description=?, schedule=? WHERE id=?",
                          (title, genre, description, schedule, movie_id))
                conn.commit()
                conn.close()
                refresh_movies()
                messagebox.showinfo("Успех", "Фильм обновлен")
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
        else:
            messagebox.showerror("Ошибка", "Выберите фильм для редактирования")

    def delete_movie():
        selected_item = tree_movies.selection()
        if selected_item:
            movie_id = tree_movies.item(selected_item)['values'][0]
            conn = sqlite3.connect('cinema.db')
            c = conn.cursor()
            c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
            conn.commit()
            conn.close()
            refresh_movies()
            messagebox.showinfo("Успех", "Фильм удален из афиши")
        else:
            messagebox.showerror("Ошибка", "Выберите фильм для удаления")

    def refresh_movies():
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT * FROM movies")
        movies = c.fetchall()
        conn.close()

        tree_movies.delete(*tree_movies.get_children())
        for movie in movies:
            tree_movies.insert('', 'end', values=movie)

    admin_window = tk.Toplevel()
    admin_window.title("Управление афишей")

    tk.Label(admin_window, text="Управление фильмами:").pack()

    tree_movies = ttk.Treeview(admin_window, columns=("ID", "Название", "Жанр", "Описание", "Расписание", "Статус"),
                               show='headings')
    for col in tree_movies["columns"]:
        tree_movies.heading(col, text=col)
    tree_movies.pack()

    tk.Label(admin_window, text="Название:").pack()
    entry_title = tk.Entry(admin_window)
    entry_title.pack()

    tk.Label(admin_window, text="Жанр:").pack()
    entry_genre = tk.Entry(admin_window)
    entry_genre.pack()

    tk.Label(admin_window, text="Описание:").pack()
    entry_description = tk.Entry(admin_window)
    entry_description.pack()

    tk.Label(admin_window, text="Расписание:").pack()
    entry_schedule = tk.Entry(admin_window)
    entry_schedule.pack()

    tk.Button(admin_window, text="Добавить фильм", command=add_movie).pack()
    tk.Button(admin_window, text="Редактировать фильм", command=edit_movie).pack()
    tk.Button(admin_window, text="Удалить фильм", command=delete_movie).pack()
    tk.Button(admin_window, text="Обновить список", command=refresh_movies).pack()

    refresh_movies()


# Интерфейс сотрудника
def employee_interface():
    def update_status():
        selected_item = tree_movies.selection()
        if selected_item:
            movie_id = tree_movies.item(selected_item)['values'][0]
            new_status = combo_status.get()
            conn = sqlite3.connect('cinema.db')
            c = conn.cursor()
            c.execute("UPDATE movies SET status=? WHERE id=?", (new_status, movie_id))
            conn.commit()
            conn.close()
            refresh_movies()
            messagebox.showinfo("Успех", "Статус фильма обновлен")
        else:
            messagebox.showerror("Ошибка", "Выберите фильм для обновления статуса")

    def refresh_movies():
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT * FROM movies")
        movies = c.fetchall()
        conn.close()

        tree_movies.delete(*tree_movies.get_children())
        for movie in movies:
            tree_movies.insert('', 'end', values=movie)

    employee_window = tk.Toplevel()
    employee_window.title("Управление текущими сеансами")

    tree_movies = ttk.Treeview(employee_window, columns=("ID", "Название", "Жанр", "Описание", "Расписание", "Статус"),
                               show='headings')
    for col in tree_movies["columns"]:
        tree_movies.heading(col, text=col)
    tree_movies.pack()

    tk.Label(employee_window, text="Обновить статус сеанса:").pack()
    combo_status = ttk.Combobox(employee_window, values=["доступен", "идет", "завершен"])
    combo_status.pack()

    tk.Button(employee_window, text="Обновить статус", command=update_status).pack()
    tk.Button(employee_window, text="Обновить список", command=refresh_movies).pack()

    refresh_movies()


# Главный экран
root = tk.Tk()
root.title("Афиша регистрация")

tk.Label(root, text="Имя пользователя:").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Пароль:").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Войти", command=login_user).pack()
tk.Button(root, text="Регистрация", command=register_user).pack()

initialize_database()
root.mainloop()
