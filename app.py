import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
import psycopg2
from psycopg2 import sql
from tkcalendar import DateEntry
import sqlparse
from datetime import date

class RusswimmingApp:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.user_role = None # Логин и роль
        self.user_password = None # Пароль
        self.athlete_names = []
        self.competition_names = []
        
        self.root = tk.Tk()
        self.root.title("Russwimming App")
        
        self.create_login_widgets()
        
        self.root.mainloop()

    def create_login_widgets(self):
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

    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        self.user_role = login
        self.user_password = password
        
        try:
            self.conn = psycopg2.connect(
                    dbname='russwimming_db',
                    user=self.user_role,
                    password=self.user_password,
                    host='localhost',
                    port='5432'
            )
            self.cursor = self.conn.cursor()
            if self.user_role == "administrator":
                messagebox.showinfo("Авторизация", "Вы вошли как администратор")
            elif self.user_role == "avg_user":
                messagebox.showinfo("Авторизация", "Вы вошли как пользователь")
            self.create_main_widgets()

        except Exception as e:
            messagebox.showerror("Ошибка авторизации", "Неверный логин или пароль")

    def create_main_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        frame.configure(bg='lightblue')

        if self.user_role == "administrator":
            tk.Button(frame, text="Создать базу данных", command=self.create_database).pack(pady=5)
            tk.Button(frame, text="Удалить базу данных", command=self.delete_database).pack(pady=5)
            tk.Button(frame, text="Добавление спортсмена", command=self.create_athlete).pack(pady=5)
            tk.Button(frame, text="Добавление соревнования", command=self.create_competition).pack(pady=5)
            tk.Button(frame, text="Добавление результата", command=self.create_result).pack(pady=5)
            tk.Button(frame, text="Добавление региона", command=self.create_region).pack(pady=5)
            tk.Button(frame, text="Редактирование данных спортсмена", command=self.change_delete_athlete).pack(pady=5)
            # tk.Button(frame, text="Удаление региона", command=self.remove_region).pack(pady=5)
            tk.Button(frame, text="Удаление всех спортсменов", command=self.clear_athlete_data).pack(pady=5)
            tk.Button(frame, text="Удаление всех данных", command=self.clear_all_data).pack(pady=(5, 30))

        tk.Button(frame, text="Поиск лучших результатов", command=self.search_rating).pack(pady=5)
        tk.Button(frame, text="Поиск результатов спортсмена", command=self.search_athlete).pack(pady=5)

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

        tk.Label(frame, text="Федеральный округ или город Федерального значения", bg='lightblue').pack()
        self.federal_district_entry = ttk.Combobox(frame, values=["ЦФО", "ПФО", "СЗФО", "ЮФО, СКФО и Севастополь", "УрФО", "СФО", "ДВФО", "Москва", "Санкт-Петербург"], state='readonly')
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
        self.rank_entry = ttk.Combobox(frame, values=["ЗМС", "МСМК", "МС", "КМС", "I", "II"], state='readonly')
        self.rank_entry.pack(pady=5)

        tk.Label(frame, text="Пол", bg='lightblue').pack()
        self.gender_entry = ttk.Combobox(frame, values=["М", "Ж"], state='readonly')
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
        self.competition_level_entry = ttk.Combobox(frame, values=["Международный", "Всероссийский", "Межрегиональный", "Региональный"], state='readonly')
        self.competition_level_entry.pack(pady=5)

        tk.Label(frame, text="Дата начала", bg='lightblue').pack()
        self.begin_date_entry = DateEntry(frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/mm/yyyy')
        self.begin_date_entry.pack(pady=5)

        tk.Label(frame, text="Дата окончания", bg='lightblue').pack()
        self.end_date_entry = DateEntry(frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/mm/yyyy')
        self.end_date_entry.pack(pady=5)

        tk.Label(frame, text="Возрастная группа", bg='lightblue').pack()
        self.age_group_entry = ttk.Combobox(frame, values=["Мужчины, женщины", "Юниоры, юниорки (16-18 лет)", "Юноши, девушки (14-15 лет)", "Юноши, девушки (11-13 лет)"], state='readonly')
        self.age_group_entry.pack(pady=5)

        tk.Label(frame, text="Бассейн, м", bg='lightblue').pack()
        self.pool_length_entry = ttk.Combobox(frame, values=[25, 50], state='readonly')
        self.pool_length_entry.pack(pady=5)

        tk.Button(frame, text="Добавить соревнование", command=lambda:self.add_competition(create_window)).pack(pady=5)

    def create_result(self):
        create_window = Toplevel(self.root)
        create_window.title("Добавление результата")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Длина дисциплины, м", bg='lightblue').pack()
        self.discipline_length_entry = ttk.Combobox(frame, values=[50, 100, 200, 400, 800, 1500], state='readonly')
        self.discipline_length_entry.pack(pady=5)

        tk.Label(frame, text="Стиль дисциплины", bg='lightblue').pack()
        self.discipline_style_entry = ttk.Combobox(frame, values=["Баттерфляй", "На спине", "Брасс", "Вольный стиль", "Комплекс"], state='readonly')
        self.discipline_style_entry.pack(pady=5)

        tk.Label(frame, text="Результат", bg='lightblue').pack()
        self.time_result_entry = tk.Entry(frame)
        self.time_result_entry.pack(pady=5)

        tk.Label(frame, text="Очки", bg='lightblue').pack()
        self.points_entry = tk.Entry(frame)
        self.points_entry.pack(pady=5)

        tk.Label(frame, text="Дата", bg='lightblue').pack()
        self.result_date_entry = DateEntry(frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/mm/yyyy')
        self.result_date_entry.pack(pady=5)

        tk.Label(frame, text="Позиция (место)", bg='lightblue').pack()
        self.place_entry = tk.Entry(frame)
        self.place_entry.pack(pady=5)

        tk.Label(frame, text="Соревнование", bg='lightblue').pack()
        competitions = self.get_competitions()
        self.competition_names = [(id_competition, f"{title} ({city}, {begin_date} - {end_date}, {pool_length} м)")
                             for id_competition, title, city, begin_date, end_date, pool_length in competitions]
        display_competition_names = [competition_name for _, competition_name in self.competition_names]
        self.competition_id_entry = ttk.Combobox(frame, values=display_competition_names, state='readonly', width=60)
        self.competition_id_entry.pack(pady=5)

        tk.Label(frame, text="Спортсмен", bg='lightblue').pack()
        athletes = self.get_athletes()
        self.athlete_names = [(id_athlete, f"{surname} {athlete_name} ({birth_year}, {rank}, {gender}, {code_region})")
                         for id_athlete, surname, athlete_name, birth_year, rank, gender, code_region in athletes]
        display_athlete_names = [athlete_name for _, athlete_name in self.athlete_names]
        self.athlete_id_entry = ttk.Combobox(frame, values=display_athlete_names, state='readonly', width=40)
        self.athlete_id_entry.pack(pady=5)

        tk.Button(frame, text="Добавить результат", command=lambda:self.add_result(create_window)).pack(pady=5)

    def search_rating(self):
        create_window = Toplevel(self.root)
        create_window.title("Поиск лучших результатов")

        create_window.configure(bg='lightblue')
        frame = tk.Frame(create_window, bg='lightblue')
        frame.pack(expand=True)

        tk.Label(frame, text="Интересующие даты", bg='lightblue').pack()
        self.rating_begin_date_entry = DateEntry(frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/mm/yyyy')
        self.rating_begin_date_entry.pack(pady=5)

        self.rating_end_date_entry = DateEntry(frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/mm/yyyy')
        self.rating_end_date_entry.pack(pady=5)

        tk.Label(frame, text="Возраст", bg='lightblue').pack()
        self.min_age_entry = tk.Entry(frame)
        self.min_age_entry.pack(pady=5)

        self.max_age_entry = tk.Entry(frame)
        self.max_age_entry.pack(pady=5)

        tk.Label(frame, text="Пол", bg='lightblue').pack()
        self.rating_gender_entry = ttk.Combobox(frame, values=["М", "Ж"], state='readonly')
        self.rating_gender_entry.pack(pady=5)

        tk.Label(frame, text="Дисциплина", bg='lightblue').pack()
        self.rating_discipline_length_entry = ttk.Combobox(frame, values=[50, 100, 200, 400, 800, 1500], state='readonly')
        self.rating_discipline_length_entry.pack(pady=5)

        self.rating_discipline_style_entry = ttk.Combobox(frame, values=["Баттерфляй", "На спине", "Брасс", "Вольный стиль", "Комплекс"], state='readonly')
        self.rating_discipline_style_entry.pack(pady=5)

        tk.Label(frame, text="Бассейн", bg='lightblue').pack()
        self.rating_pool_length_entry = ttk.Combobox(frame, values=[25, 50], state='readonly')
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
        self.search_gender_entry = ttk.Combobox(frame, values=["М", "Ж"], state='readonly')
        self.search_gender_entry.pack(pady=5)

        tk.Label(frame, text="Год рождения", bg='lightblue').pack()
        self.search_b_y_entry = tk.Entry(frame)
        self.search_b_y_entry.pack(pady=5)

        tk.Label(frame, text="Разряд", bg='lightblue').pack()
        self.search_rank_entry = ttk.Combobox(frame, values=["ЗМС", "МСМК", "МС", "КМС", "I", "II"], state='readonly')
        self.search_rank_entry.pack(pady=5)

        tk.Label(frame, text="Код региона", bg='lightblue').pack()
        self.search_c_r_entry = tk.Entry(frame)
        self.search_c_r_entry.pack(pady=5)

        tk.Button(frame, text="Показать результаты", command=lambda:self.get_athlete_results(create_window)).pack(pady=5)

    def change_delete_athlete(self):
        create_window = Toplevel(self.root)
        create_window.title("Поиск спортсмена для редактирования его данных")

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
        self.cd_gender_entry = ttk.Combobox(frame, values=["М", "Ж"], state='readonly')
        self.cd_gender_entry.pack(pady=5)

        tk.Label(frame, text="Год рождения", bg='lightblue').pack()
        self.cd_birth_year_entry = tk.Entry(frame)
        self.cd_birth_year_entry.pack(pady=5)

        tk.Label(frame, text="Разряд", bg='lightblue').pack()
        self.cd_rank_entry = ttk.Combobox(frame, values=["ЗМС", "МСМК", "МС", "КМС", "I", "II"], state='readonly')
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
            """conn = psycopg2.connect(user="postgres", password="postgres", host="localhost", port="5432")"""
            conn = psycopg2.connect(user=self.user_role, password=self.user_password, host="localhost", port="5432", dbname="russwimming_db")
            """conn.autocommit = True"""
            cursor = conn.cursor()
            """createdb_file = open('scripts/createdb.sql', 'r')
            createdb = createdb_file.read()
            cursor.execute(createdb)
            cursor.close()
            conn.close()
            conn = psycopg2.connect(user="postgres", password="postgres", host="localhost", port="5432", dbname="russwimming_db")
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
            cursor.execute(getResults)"""
            
            query = sql.SQL("SELECT create_tables()")
            cursor.execute(query)
            conn.commit()

            messagebox.showinfo("Информация", "База данных создана.")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        finally:
            cursor.close()
            conn.close()

    def delete_database(self):
        try:
            conn = psycopg2.connect(user=self.user_role, password=self.user_password, host="localhost", port="5432", dbname="russwimming_db")
            """conn = psycopg2.connect(user="postgres", password="postgres", host="localhost", port="5432")
            conn.autocommit = True"""
            cursor = conn.cursor()

            """deletedb_file = open('scripts/deletedb.sql', 'r')
            deletedb = deletedb_file.read()
            cursor.execute(deletedb)

            drop_roles_file = open('scripts/drop_roles.sql', 'r')
            drop_roles = drop_roles_file.read()
            cursor.execute(drop_roles)"""

            query = sql.SQL("SELECT drop_tables()")
            cursor.execute(query)
            conn.commit()
            
            messagebox.showinfo("Информация", "База данных удалена.")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        finally:
            cursor.close()
            conn.close()

    def add_region(self, create_window):
        if not self.connect_db():
            return
        
        region_code = self.region_code_entry.get().strip()
        region_name = self.region_name_entry.get().strip()
        federal_district = self.federal_district_entry.get()
        team_leader = self.team_leader_entry.get().strip()

        if len(region_code) > 3:
            messagebox.showerror("Ошибка", "Некорректное значение кода региона")
            create_window.destroy()
            return

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
        try:
            birth_year = int(self.birth_year_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return
        rank = self.rank_entry.get()
        gender = self.gender_entry.get()
        code_region = self.code_region_entry.get().strip()

        today = date.today()
        if birth_year < 1908 or birth_year > today.year:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return

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
        competition_level = self.competition_level_entry.get()
        begin_date = self.begin_date_entry.get()
        end_date = self.end_date_entry.get()
        age_group = self.age_group_entry.get()
        pool_length = self.pool_length_entry.get()

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
        
        discipline_length = self.discipline_length_entry.get()
        discipline_style = self.discipline_style_entry.get()
        time_result = self.time_result_entry.get().strip()
        try:
            points = int(self.points_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение очков World Aquatics")
            create_window.destroy()
            return
        result_date = self.result_date_entry.get()
        try:
            place = int(self.place_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение места (позиции)")
            create_window.destroy()
            return
        selected_competition_name = self.competition_id_entry.get()
        competition_id = next((id_competition for id_competition, competition_name in self.competition_names if competition_name == selected_competition_name), None)
        selected_athlete_name = self.athlete_id_entry.get()
        athlete_id = next((id_athlete for id_athlete, athlete_name in self.athlete_names if athlete_name == selected_athlete_name), None)
       
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
        
        rating_begin_date = self.rating_begin_date_entry.get()
        rating_end_date = self.rating_end_date_entry.get()
        try:
            min_age = int(self.min_age_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение минимального возраста")
            create_window.destroy()
            return
        try:
            max_age = int(self.max_age_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение максимального возраста")
            create_window.destroy()
            return
        rating_gender = self.rating_gender_entry.get()
        rating_discipline_length = self.rating_discipline_length_entry.get()
        rating_discipline_style = self.rating_discipline_style_entry.get()
        rating_pool_length = self.rating_pool_length_entry.get()

        """if min_age == "":
            min_age = 0
        
        if max_age == "":
            max_age = 100"""
        
        if min_age > 116:
            messagebox.showerror("Ошибка", "Некорректное значение минимального возраста")
            create_window.destroy()
            return

        if max_age > 116:
            messagebox.showerror("Ошибка", "Некорректное значение максимального возраста")
            create_window.destroy()
            return

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
        try:
            cd_birth_year = int(self.cd_birth_year_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return
        cd_rank = self.cd_rank_entry.get()
        cd_gender = self.cd_gender_entry.get()
        cd_code_region = self.cd_code_region_entry.get()

        today = date.today()
        if cd_birth_year < 1908 or cd_birth_year > today.year:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return

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
        try:
            cd_birth_year = int(self.cd_birth_year_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return
        cd_rank = self.cd_rank_entry.get()
        cd_gender = self.cd_gender_entry.get()
        cd_code_region = self.cd_code_region_entry.get()

        today = date.today()
        if cd_birth_year < 1908 or cd_birth_year > today.year:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return

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
        new_rank_entry = ttk.Combobox(frame, values=["ЗМС", "МСМК", "МС", "КМС", "I", "II"], state='readonly')
        new_rank_entry.pack(pady=5)
 
        tk.Label(frame, text="Пол", bg='lightblue').pack()
        new_gender_entry = ttk.Combobox(frame, values=["М", "Ж"], state='readonly')
        new_gender_entry.pack(pady=5)

        tk.Label(frame, text="Код региона", bg='lightblue').pack()
        new_code_region_entry = tk.Entry(frame)
        new_code_region_entry.pack(pady=5)

        def update_athlete_data():
            new_surname = new_surname_entry.get().strip()
            new_name = new_name_entry.get().strip()
            try:
                new_birth_year = new_birth_year_entry.get().strip()
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректное значение года рождения")
                update_window.destroy()
                return
            new_rank = new_rank_entry.get()
            new_gender = new_gender_entry.get()
            new_code_region = new_code_region_entry.get()

            today = date.today()
            if new_birth_year < 1908 or new_birth_year > today.year:
                messagebox.showerror("Ошибка", "Некорректное значение года рождения")
                update_window.destroy()
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
        search_gender = self.search_gender_entry.get()
        try:
            search_b_y = int(self.search_b_y_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return
        search_rank = self.search_rank_entry.get()
        search_c_r = self.search_c_r_entry.get()

        today = date.today()
        if search_b_y < 1908 or search_b_y > today.year:
            messagebox.showerror("Ошибка", "Некорректное значение года рождения")
            create_window.destroy()
            return

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

    def get_athletes(self):
        if not self.connect_db():
            return

        try:
            query = sql.SQL("SELECT * FROM get_athletes()")
            self.cursor.execute(query)
            athletes = self.cursor.fetchall()
            return athletes

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def get_competitions(self):
        if not self.connect_db():
            return

        try:
            query = sql.SQL("SELECT * FROM get_competitions()")
            self.cursor.execute(query)
            competitions = self.cursor.fetchall()
            return competitions

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    app = RusswimmingApp()