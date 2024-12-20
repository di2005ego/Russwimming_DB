import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
import psycopg2
from psycopg2 import sql
import sqlparse

class RusswimmingApp:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.user_role = None # Логин и роль
        self.user_password = None # Пароль
        
        self.root = tk.Tk()
        self.root.title("Russwimming App")
        
        self.create_login_widgets()
        
        self.root.mainloop()

    def create_login_widgets(self): # Виджет для авторизации
        self.root.configure(bg='lightblue')
        frame = tk.Frame(self.root, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Логин", bg='lightblue').pack(pady=5)
        self.login_entry = tk.Entry(frame)
        self.login_entry.pack(pady=5)

        tk.Label(frame, text="Пароль", bg='lightblue').pack(pady=5)
        self.password_entry = tk.Entry(frame, show='•')
        self.password_entry.pack(pady=5)

        tk.Button(frame, text="Войти", command=self.login).pack(pady=10)

    def login(self): # Авторизация
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        self.user_password = password

        if login == "administrator" and password == "di_ego":
            self.user_role = "administrator"
            messagebox.showinfo("Авторизация", "Вы вошли как администратор.")
            self.create_main_widgets()
        elif login == "avg_user" and password == "userxfa":
            self.user_role = "avg_user"
            messagebox.showinfo("Авторизация", "Вы вошли как пользователь.")
            self.create_main_widgets()
        else:
            messagebox.showerror("Ошибка авторизации", "Неверный логин или пароль.")

    def create_main_widgets(self): # Основное окно
        # Удаляем все виджеты авторизации
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        frame.configure(bg='lightblue')

        # Кнопки для управления базой данных
        if self.user_role == "administrator":
            tk.Button(frame, text="Создать базу данных", command=self.create_database).pack(pady=5)
            tk.Button(frame, text="Удалить базу данных", command=self.delete_database).pack(pady=5)
            tk.Button(frame, text="Добавление спортсмена", command=self.create_athlete).pack(pady=5)
            tk.Button(frame, text="Добавление соревнования", command=self.create_competition).pack(pady=5)
            tk.Button(frame, text="Добавление результата", command=self.create_result).pack(pady=5)
            tk.Button(frame, text="Добавление региона", command=self.create_region).pack(pady=5)

        tk.Button(frame, text="Поиск лучших результатов", command=self.search_rating).pack(pady=5)
        tk.Button(frame, text="Поиск результатов спортсмена", command=self.search_athlete).pack(pady=5)
        if self.user_role == "administrator":
            tk.Button(frame, text="Редактирование или удаление спортсмена", command=self.change_delete_athlete).pack(pady=5)
            tk.Button(frame, text="Удаление всех спортсменов", command=self.clear_athlete_data).pack(pady=5)
            tk.Button(frame, text="Удаление всех данных", command=self.clear_all_data).pack(pady=5)

    def clear_all_data(self):
        if not self.connect_db():
            return

        try:
            query = sql.SQL("SELECT clear_all_data()")
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Информация", "Данные удалены.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def clear_athlete_data(self):
        if not self.connect_db():
            return

        try:
            query = sql.SQL("SELECT clear_athlete_data()")
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Информация", "Спортсмены удалены.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def create_region(self):
        create_window = Toplevel(self.root)
        create_window.title("Добавление региона")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Код", bg='lightblue').pack()
        self.region_code_entry = tk.Entry(frame)
        self.region_code_entry.pack(pady=5)

        tk.Label(frame, text="Название", bg='lightblue').pack()
        self.region_name_entry = tk.Entry(frame)
        self.region_name_entry.pack(pady=5)

        tk.Label(frame, text="Федеральный округ", bg='lightblue').pack()
        self.federal_district_entry = tk.Entry(frame)
        self.federal_district_entry.pack(pady=5)

        tk.Label(frame, text="Руководитель", bg='lightblue').pack()
        self.team_leader_entry = tk.Entry(frame)
        self.team_leader_entry.pack(pady=5)

        tk.Button(frame, text="Добавить регион", command=lambda:self.add_region(create_window)).pack(pady=5)

    def create_athlete(self):
        create_window = Toplevel(self.root)
        create_window.title("Добавление спортсмена")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Фамилия", bg='lightblue').pack()
        self.surname_entry = tk.Entry(frame)
        self.surname_entry.pack(pady=5)

        tk.Label(frame, text="Имя", bg='lightblue').pack()
        self.athlete_name_entry = tk.Entry(frame)
        self.athlete_name_entry.pack(pady=5)

        tk.Label(frame, text="Год рождения", bg='lightblue').pack()
        self.birth_year_entry = tk.Entry(frame)
        self.birth_year_entry.pack(pady=5)

        tk.Label(frame, text="Разряд", bg='lightblue').pack()
        self.rank_entry = tk.Entry(frame)
        self.rank_entry.pack(pady=5)

        tk.Label(frame, text="Пол (М/Ж)", bg='lightblue').pack()
        self.gender_entry = tk.Entry(frame)
        self.gender_entry.pack(pady=5)

        tk.Label(frame, text="Код региона", bg='lightblue').pack()
        self.code_region_entry = tk.Entry(frame)
        self.code_region_entry.pack(pady=5)

        tk.Button(frame, text="Добавить спортсмена", command=lambda:self.add_athlete(create_window)).pack(pady=5)

    def create_competition(self):
        create_window = Toplevel(self.root)
        create_window.title("Добавление соревнования")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Название", bg='lightblue').pack()
        self.title_entry = tk.Entry(frame)
        self.title_entry.pack(pady=5)

        tk.Label(frame, text="Город", bg='lightblue').pack()
        self.city_entry = tk.Entry(frame)
        self.city_entry.pack(pady=5)

        tk.Label(frame, text="Уровень", bg='lightblue').pack()
        self.competition_level_entry = tk.Entry(frame)
        self.competition_level_entry.pack(pady=5)

        tk.Label(frame, text="Дата начала", bg='lightblue').pack()
        self.begin_date_entry = tk.Entry(frame)
        self.begin_date_entry.pack(pady=5)

        tk.Label(frame, text="Дата окончания", bg='lightblue').pack()
        self.end_date_entry = tk.Entry(frame)
        self.end_date_entry.pack(pady=5)

        tk.Label(frame, text="Возрастная группа", bg='lightblue').pack()
        self.age_group_entry = tk.Entry(frame)
        self.age_group_entry.pack(pady=5)

        tk.Label(frame, text="Бассейн", bg='lightblue').pack()
        self.pool_length_entry = tk.Entry(frame)
        self.pool_length_entry.pack(pady=5)

        tk.Button(frame, text="Добавить соревнование", command=lambda:self.add_competition(create_window)).pack(pady=5)

    def create_result(self):
        create_window = Toplevel(self.root)
        create_window.title("Добавление результата")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Длина дисциплины, м", bg='lightblue').pack()
        self.discipline_length_entry = tk.Entry(frame)
        self.discipline_length_entry.pack(pady=5)

        tk.Label(frame, text="Стиль дисциплины", bg='lightblue').pack()
        self.discipline_style_entry = tk.Entry(frame)
        self.discipline_style_entry.pack(pady=5)

        tk.Label(frame, text="Результат", bg='lightblue').pack()
        self.time_result_entry = tk.Entry(frame)
        self.time_result_entry.pack(pady=5)

        tk.Label(frame, text="Очки", bg='lightblue').pack()
        self.points_entry = tk.Entry(frame)
        self.points_entry.pack(pady=5)

        tk.Label(frame, text="Дата", bg='lightblue').pack()
        self.result_date_entry = tk.Entry(frame)
        self.result_date_entry.pack(pady=5)

        tk.Label(frame, text="Позиция (место)", bg='lightblue').pack()
        self.place_entry = tk.Entry(frame)
        self.place_entry.pack(pady=5)

        tk.Label(frame, text="ID соревнования", bg='lightblue').pack()
        self.competition_id_entry = tk.Entry(frame)
        self.competition_id_entry.pack(pady=5)

        tk.Label(frame, text="ID спортсмена", bg='lightblue').pack()
        self.athlete_id_entry = tk.Entry(frame)
        self.athlete_id_entry.pack(pady=5)

        tk.Button(frame, text="Добавить результат", command=lambda:self.add_result(create_window)).pack(pady=5)

    def search_rating(self):
        create_window = Toplevel(self.root)
        create_window.title("Поиск лучших результатов")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Интересующие даты", bg='lightblue').pack()
        self.rating_begin_date_entry = tk.Entry(frame)
        self.rating_begin_date_entry.pack(pady=5)

        self.rating_end_date_entry = tk.Entry(frame)
        self.rating_end_date_entry.pack(pady=5)

        tk.Label(frame, text="Возраст", bg='lightblue').pack()
        self.min_age_entry = tk.Entry(frame)
        self.min_age_entry.pack(pady=5)

        self.max_age_entry = tk.Entry(frame)
        self.max_age_entry.pack(pady=5)

        tk.Label(frame, text="Пол", bg='lightblue').pack()
        self.rating_gender_entry = tk.Entry(frame)
        self.rating_gender_entry.pack(pady=5)

        tk.Label(frame, text="Дисциплина", bg='lightblue').pack()
        self.rating_discipline_length_entry = tk.Entry(frame)
        self.rating_discipline_length_entry.pack(pady=5)

        self.rating_discipline_style_entry = tk.Entry(frame)
        self.rating_discipline_style_entry.pack(pady=5)

        tk.Label(frame, text="Бассейн", bg='lightblue').pack()
        self.rating_pool_length_entry = tk.Entry(frame)
        self.rating_pool_length_entry.pack(pady=5)

        tk.Button(frame, text="Показать результаты", command=lambda:self.get_results(create_window)).pack(pady=5)

    def search_athlete(self):
        create_window = Toplevel(self.root)
        create_window.title("Поиск результатов спортсмена")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Фамилия", bg='lightblue').pack()
        self.search_surname_entry = tk.Entry(frame)
        self.search_surname_entry.pack(pady=5)

        tk.Label(frame, text="Имя", bg='lightblue').pack()
        self.search_name_entry = tk.Entry(frame)
        self.search_name_entry.pack(pady=5)

        tk.Label(frame, text="Пол", bg='lightblue').pack()
        self.search_gender_entry = tk.Entry(frame)
        self.search_gender_entry.pack(pady=5)

        tk.Label(frame, text="Год рождения", bg='lightblue').pack()
        self.search_b_y_entry = tk.Entry(frame)
        self.search_b_y_entry.pack(pady=5)

        tk.Label(frame, text="Разряд", bg='lightblue').pack()
        self.search_rank_entry = tk.Entry(frame)
        self.search_rank_entry.pack(pady=5)

        tk.Label(frame, text="Код региона", bg='lightblue').pack()
        self.search_c_r_entry = tk.Entry(frame)
        self.search_c_r_entry.pack(pady=5)

        tk.Button(frame, text="Показать результаты", command=lambda:self.get_athlete_results(create_window)).pack(pady=5)

    def change_delete_athlete(self):
        create_window = Toplevel(self.root)
        create_window.title("Редактирование или удаление спортсмена")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Фамилия", bg='lightblue').pack()
        self.cd_surname_entry = tk.Entry(frame)
        self.cd_surname_entry.pack(pady=5)

        tk.Label(frame, text="Имя", bg='lightblue').pack()
        self.cd_name_entry = tk.Entry(frame)
        self.cd_name_entry.pack(pady=5)

        tk.Label(frame, text="Пол", bg='lightblue').pack()
        self.cd_gender_entry = tk.Entry(frame)
        self.cd_gender_entry.pack(pady=5)

        tk.Label(frame, text="Год рождения", bg='lightblue').pack()
        self.cd_birth_year_entry = tk.Entry(frame)
        self.cd_birth_year_entry.pack(pady=5)

        tk.Label(frame, text="Разряд", bg='lightblue').pack()
        self.cd_rank_entry = tk.Entry(frame)
        self.cd_rank_entry.pack(pady=5)

        tk.Label(frame, text="Код региона", bg='lightblue').pack()
        self.cd_code_region_entry = tk.Entry(frame)
        self.cd_code_region_entry.pack(pady=5)

        tk.Button(frame, text="Редактировать", command=lambda:self.change_athlete(create_window)).pack(pady=5)
        tk.Button(frame, text="Удалить", command=lambda:self.remove_athlete(create_window)).pack(pady=5)

    def connect_db(self):
        try:
            if not self.conn:
                self.conn = psycopg2.connect(
                    dbname='russwimming_db',
                    user=self.user_role,
                    password=self.user_password,
                    host='localhost',
                    port='5432'
                )
                self.cursor = self.conn.cursor()
                print("Подключение к базе данных успешно!")
            else:
                print("Подключение уже установлено.")
                
            return True
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return False

    def create_database(self):
        try:
            conn = psycopg2.connect(user="postgres",
                                    password="postgres",
                                    host="localhost",
                                    port="5432")
            conn.autocommit = True
            cursor = conn.cursor()
            createdb_file = open('scripts/createdb.sql', 'r')
            createdb = createdb_file.read()
            cursor.execute(createdb)
            cursor.close()
            conn.close()
            conn = psycopg2.connect(user="postgres",
                                    password="postgres",
                                    host="localhost",
                                    port="5432",
                                    dbname="russwimming_db")
            conn.autocommit = True
            cursor = conn.cursor()
            createdb_2_file = open('scripts/createdb_2.sql', 'r')
            createdb_2 = createdb_2_file.read()
            statements = sqlparse.split(createdb_2)
            for s in statements:
                s = s.strip()
                cursor.execute(s)

            getResults_file = open('scripts/get_results.sql', 'r')
            getResults = getResults_file.read()
            cursor.execute(getResults)
            
            messagebox.showinfo("Информация", "База данных создана.")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        finally:
            cursor.close()
            conn.close()

    def delete_database(self):
        try:
            conn = psycopg2.connect(user="postgres",
                                    password="postgres",
                                    host="localhost",
                                    port="5432")
            conn.autocommit = True
            cursor = conn.cursor()

            deletedb_file = open('scripts/deletedb.sql', 'r')
            deletedb = deletedb_file.read()
            cursor.execute(deletedb)

            drop_roles_file = open('scripts/drop_roles.sql', 'r')
            drop_roles = drop_roles_file.read()
            cursor.execute(drop_roles)

            cursor.close()
            conn.close()
            
            messagebox.showinfo("Информация", "База данных удалена.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_region(self, create_window):
        if not self.connect_db():
            return
        
        region_code = self.region_code_entry.get().strip()
        region_name = self.region_name_entry.get().strip()
        federal_district = self.federal_district_entry.get().strip()
        team_leader = self.team_leader_entry.get().strip()

        try:
            query = sql.SQL("SELECT add_region({}, {}, {}, {})").format(
                sql.Literal(region_code),
                sql.Literal(region_name),
                sql.Literal(federal_district),
                sql.Literal(team_leader),
            )
             
            self.cursor.execute(query)
            self.conn.commit()

            messagebox.showinfo("Информация", "Регион добавлен.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        finally:
            create_window.destroy()

    def add_athlete(self, create_window):
        if not self.connect_db():
            return
        
        surname = self.surname_entry.get().strip()
        athlete_name = self.athlete_name_entry.get().strip()
        birth_year = int(self.birth_year_entry.get().strip())
        rank = self.rank_entry.get().strip().upper()
        gender = self.gender_entry.get().strip().upper()
        code_region = self.code_region_entry.get().strip().upper()

        if gender not in ['М', 'Ж']:
            raise ValueError("Пол должен быть М или Ж.")

        try:
            query = sql.SQL("SELECT add_athlete({}, {}, {}, {}, {}, {})").format(
                sql.Literal(surname),
                sql.Literal(athlete_name),
                sql.Literal(birth_year),
                sql.Literal(rank),
                sql.Literal(gender),
                sql.Literal(code_region)
            )
             
            self.cursor.execute(query)
            self.conn.commit()

            messagebox.showinfo("Информация", "Спортсмен добавлен.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        
        finally:
            create_window.destroy()

    def add_competition(self, create_window):
        if not self.connect_db():
            return
        
        title = self.title_entry.get().strip()
        city = self.city_entry.get().strip()
        competition_level = self.competition_level_entry.get().strip()
        begin_date = self.begin_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        age_group = self.age_group_entry.get().strip()
        pool_length = self.pool_length_entry.get().strip()

        try:
            query = sql.SQL("SELECT add_competition({}, {}, {}, {}, {}, {}, {})").format(
                sql.Literal(title),
                sql.Literal(city),
                sql.Literal(competition_level),
                sql.Literal(begin_date),
                sql.Literal(end_date),
                sql.Literal(age_group),
                sql.Literal(pool_length)
            )
             
            self.cursor.execute(query)
            self.conn.commit()

            messagebox.showinfo("Информация", "Соревнование добавлено.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        finally:
            create_window.destroy()
    
    def add_result(self, create_window):
        if not self.connect_db():
            return
        
        discipline_length = self.discipline_length_entry.get().strip()
        discipline_style = self.discipline_style_entry.get().strip()
        time_result = self.time_result_entry.get().strip()
        points = self.points_entry.get().strip()
        result_date = self.result_date_entry.get().strip()
        place = self.place_entry.get().strip()
        competition_id = self.competition_id_entry.get().strip()
        athlete_id = self.athlete_id_entry.get().strip()

        try:
            query = sql.SQL("SELECT add_result({}, {}, {}, {}, {}, {}, {}, {})").format(
                sql.Literal(discipline_length),
                sql.Literal(discipline_style),
                sql.Literal(time_result),
                sql.Literal(points),
                sql.Literal(result_date),
                sql.Literal(place),
                sql.Literal(competition_id),
                sql.Literal(athlete_id)
            )
             
            self.cursor.execute(query)
            self.conn.commit()

            messagebox.showinfo("Информация", "Результат добавлен.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        
        finally:
            create_window.destroy()

    def get_results(self, create_window):
        if not self.connect_db():
            return
        
        rating_begin_date = self.rating_begin_date_entry.get().strip()
        rating_end_date = self.rating_end_date_entry.get().strip()
        min_age = self.min_age_entry.get().strip()
        max_age = self.max_age_entry.get().strip()
        rating_gender = self.rating_gender_entry.get().strip().upper()
        rating_discipline_length = self.rating_discipline_length_entry.get().strip()
        rating_discipline_style = self.rating_discipline_style_entry.get().strip()
        rating_pool_length = self.rating_pool_length_entry.get().strip()

        try:
            query = sql.SQL("SELECT * FROM get_results({}, {}, {}, {}, {}, {}, {}, {})").format(
                sql.Literal(rating_begin_date),
                sql.Literal(rating_end_date),
                sql.Literal(rating_discipline_length),
                sql.Literal(rating_discipline_style),
                sql.Literal(rating_gender),
                sql.Literal(rating_pool_length),
                sql.Literal(min_age),
                sql.Literal(max_age)
            )

            create_window.destroy()

            results_window = tk.Toplevel(self.root)
            results_window.title("Лучшие результаты")

            treeview = ttk.Treeview(results_window)
            treeview["columns"] = ("№", "Фамилия", "Имя", "Г.Р.", "Разряд", "Субъект РФ",
                                     "Соревнования", "Город", "Результат",
                                     "Очки WA", "Дата")
             
            for col in treeview["columns"]:
                treeview.heading(col, text=col)
                if col == "№":
                    treeview.column(col, width=5)
                elif col == "Фамилия":
                    treeview.column(col, width=100)
                elif col == "Имя":
                    treeview.column(col, width=100)
                elif col == "Г.Р.":
                    treeview.column(col, width=25)
                elif col == "Разряд":
                    treeview.column(col, width=25)
                elif col == "Субъект РФ":
                    treeview.column(col, width=200)
                elif col == "Соревнования":
                    treeview.column(col, width=245)
                elif col == "Город":
                    treeview.column(col, width=105)
                elif col == "Результат":
                    treeview.column(col, width=40)
                elif col == "Очки WA":
                    treeview.column(col, width=20)
                elif col == "Дата":
                    treeview.column(col, width=55)
             
            treeview["show"] = "headings"
            treeview.pack(expand=True, fill='both')

            self.cursor.execute(query)
            rows = self.cursor.fetchall()
             
            for row in rows:
                treeview.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def remove_athlete(self, create_window):
        if not self.connect_db():
            return
        
        cd_surname = self.cd_surname_entry.get().strip()
        cd_name = self.cd_name_entry.get().strip()
        cd_birth_year = self.cd_birth_year_entry.get().strip()
        cd_rank = self.cd_rank_entry.get().strip().upper()
        cd_gender = self.cd_gender_entry.get().strip().upper()
        cd_code_region = self.cd_code_region_entry.get().strip().upper()

        if cd_gender not in ['М', 'Ж']:
            raise ValueError("Пол должен быть М или Ж.")

        try:
            query = sql.SQL("SELECT delete_athlete({}, {}, {}, {}, {}, {})").format(
                sql.Literal(cd_surname),
                sql.Literal(cd_name),
                sql.Literal(cd_birth_year),
                sql.Literal(cd_rank),
                sql.Literal(cd_gender),
                sql.Literal(cd_code_region)
            )
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Информация", "Спортсмен удален.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        
        finally:
            create_window.destroy()

    def change_athlete(self, create_window):
        if not self.connect_db():
            return
        
        cd_surname = self.cd_surname_entry.get().strip()
        cd_name = self.cd_name_entry.get().strip()
        cd_birth_year = self.cd_birth_year_entry.get().strip()
        cd_rank = self.cd_rank_entry.get().strip().upper()
        cd_gender = self.cd_gender_entry.get().strip().upper()
        cd_code_region = self.cd_code_region_entry.get().strip().upper()

        if cd_gender not in ['М', 'Ж']:
            raise ValueError("Пол должен быть М или Ж.")

        try:
            query = sql.SQL("SELECT get_athlete_id({}, {}, {}, {}, {}, {})").format(
                sql.Literal(cd_surname),
                sql.Literal(cd_name),
                sql.Literal(cd_birth_year),
                sql.Literal(cd_rank),
                sql.Literal(cd_gender),
                sql.Literal(cd_code_region)
            )
            self.cursor.execute(query)
            cd_id = self.cursor.fetchone()
            if cd_id is None:
                messagebox.showerror("Ошибка", "Спортсмен не найден.")
                return
            
            self.update_window(cd_id)
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        
        finally:
            create_window.destroy()
    
    def update_window(self, cd_id):
        update_window = Toplevel(self.root)
        update_window.title("Редактирование спортсмена")

        update_window.configure(bg='lightblue')
        frame = tk.Frame(update_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Фамилия", bg='lightblue').pack()
        new_surname_entry = tk.Entry(frame)
        new_surname_entry.pack(pady=5)

        tk.Label(frame, text="Имя", bg='lightblue').pack()
        new_name_entry = tk.Entry(frame)
        new_name_entry.pack(pady=5)

        tk.Label(frame, text="Год рождения", bg='lightblue').pack()
        new_birth_year_entry = tk.Entry(frame)
        new_birth_year_entry.pack(pady=5)

        tk.Label(frame, text="Разряд", bg='lightblue').pack()
        new_rank_entry = tk.Entry(frame)
        new_rank_entry.pack(pady=5)
 
        tk.Label(frame, text="Пол (M/F)", bg='lightblue').pack()
        new_gender_entry = tk.Entry(frame)
        new_gender_entry.pack(pady=5)

        tk.Label(frame, text="Код региона", bg='lightblue').pack()
        new_code_region_entry = tk.Entry(frame)
        new_code_region_entry.pack(pady=5)

        def update_athlete_data():
            new_surname = new_surname_entry.get().strip()
            new_name = new_name_entry.get().strip()
            new_birth_year = new_birth_year_entry.get().strip()
            new_rank = new_rank_entry.get().strip().upper()
            new_gender = new_gender_entry.get().strip().upper()
            new_code_region = new_code_region_entry.get().strip().upper()

            if new_gender not in ['М', 'Ж']:
               messagebox.showerror("Ошибка", "Пол должен быть М или Ж.")
               return

            try:
                update_query = sql.SQL("SELECT update_athlete({}, {}, {}, {}, {}, {}, {})").format(
                    sql.Literal(cd_id),
                    sql.Literal(new_surname),
                    sql.Literal(new_name),
                    sql.Literal(new_birth_year),
                    sql.Literal(new_rank),
                    sql.Literal(new_gender),
                    sql.Literal(new_code_region)
                )
                self.cursor.execute(update_query)
                self.conn.commit()

                messagebox.showinfo("Успех", "Данные спортсмена успешно обновлены.")
                update_window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(frame, text="Обновить", command=update_athlete_data).pack(pady=10)

    def get_athlete_results(self, create_window):
        if not self.connect_db():
            return
        
        search_surname = self.search_surname_entry.get().strip()
        search_name = self.search_name_entry.get().strip()
        search_gender = self.search_gender_entry.get().strip().upper()
        search_b_y = self.search_b_y_entry.get().strip()
        search_rank = self.search_rank_entry.get().strip().upper()
        search_c_r = self.search_c_r_entry.get().strip().upper()

        try:
            query = sql.SQL("SELECT * FROM get_athlete_results({}, {}, {}, {}, {}, {})").format(
                sql.Literal(search_surname),
                sql.Literal(search_name),
                sql.Literal(search_b_y),
                sql.Literal(search_rank),
                sql.Literal(search_gender),
                sql.Literal(search_c_r)
            )

            create_window.destroy()

            results_window = tk.Toplevel(self.root)
            results_window.title("Результаты спортсмена")

            treeview = ttk.Treeview(results_window)
            treeview["columns"] = ("Дистанция", "Стиль", "Соревнование", "Бассейн", "Результат", "Очки",
                                     "Дата", "Позиция (место)")
             
            for col in treeview["columns"]:
                treeview.heading(col, text=col)
                if col == "Дистанция":
                    treeview.column(col, width=25)
                elif col == "Стиль":
                    treeview.column(col, width=70)
                elif col == "Соревнование":
                    treeview.column(col, width=300)
                elif col == "Бассейн":
                    treeview.column(col, width=10)
                elif col == "Результат":
                    treeview.column(col, width=60)
                elif col == "Очки":
                    treeview.column(col, width=25)
                elif col == "Дата":
                    treeview.column(col, width=50)
                elif col == "Позиция (место)":
                    treeview.column(col, width=25)
             
            treeview["show"] = "headings"
            treeview.pack(expand=True, fill='both')

            self.cursor.execute(query)
            rows = self.cursor.fetchall()
             
            for row in rows:
                treeview.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    app = RusswimmingApp()