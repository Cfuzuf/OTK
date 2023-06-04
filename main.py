import json
import sqlite3
import os.path
import datetime
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.core.clipboard import Clipboard

import platform
if platform.system() == "Windows" or platform.system() == "Linux":
    from kivy.core.window import Window
    Window.size = (1080/3, 2160/3)


class MyScreenManager(ScreenManager):
    pass


class Menu(Screen):
    pass


class Setting(Screen):
    pass


class Day(Screen):
    pass


class ShowSelectionFromDatabase(Screen):
    pass


class EditingRecordInDatabase(Screen):
    pass


class ViewingRecordsFromDatabase(Screen):
    pass


class MainApp(MDApp):
    settings = {
        "fuel_consumption_per_100_km": "Не настроено",
        "work_shift_cost": "Не настроено"
    }
    day = {
        "date": "Дата",
        "start": "0",
        "stop": "0",
        "total": "0",
        "route": " ",
        "fueling_in_liters": "0",
        "fueling_in_rubles": "0",
        "fuel_card_balance": "Не задано..."
    }

    if not os.path.isfile("./settings.json"):
        with open("./settings.json", "w") as file:
            json.dump(settings, file, indent=4)
    else:
        with open("./settings.json", "r") as file:
            settings = json.load(file)

    if not os.path.isfile("./day.json"):
        with open("./day.json", "w") as file:
            json.dump(day, file, indent=4)
    else:
        with open("./day.json", "r") as file:
            day = json.load(file)

    def show_date_picker(self, mode):
        if mode == "day":
            date_picker = MDDatePicker(
                title="Выберите сегодняшнюю дату"
            )
            date_picker.bind(on_save=self.pick_date)
            date_picker.open()
        elif mode == "editing":
            recording_date = MDDatePicker(
                title="Выберите дату для редактирования"
            )
            recording_date.bind(on_save=self.pick_editing_date)
            recording_date.open()
        elif mode == "view":
            recording_date = MDDatePicker(
                title="""Выберите дату или диапазон дат
для просмотра""",
                mode="range"
            )
            recording_date.bind(on_save=self.pick_view_record)
            recording_date.open()

    def pick_date(self, *args):
        date = ".".join(reversed(str(args[1]).split("-")))
        self.root.ids.date.text = date
        self.day["date"] = date
        self.update_day_json()

    def pick_editing_date(self, *args):
        date = ".".join(reversed(str(args[1]).split("-")))
        with sqlite3.connect("driving_statistics.db") as db:
            cursor = db.cursor()
            try:
                recording = cursor.execute(
                    "SELECT * FROM my_statistics WHERE date=?", (date,)
                )
                data = recording.fetchone()
            except Exception as e:
                print(e)

        if data is not None:
            self.load_editing_day(data)
        else:
            self.show_alert_dialog_record_does_not_exist()

    def pick_view_record(self, *args):
        self.date_list = [".".join(reversed(str(x).split("-")))
                          for x in map(str, args[-1][::len(args[-1])-1])]

        with sqlite3.connect("driving_statistics.db") as db:
            cursor = db.cursor()
            try:
                recording = cursor.execute(
                    """SELECT * FROM my_statistics WHERE date BETWEEN ? AND ?""",
                    self.date_list
                )
                self.viewed_records_list = recording.fetchall()
            except Exception as e:
                print(e)

        if self.viewed_records_list:
            self.load_viewed_records()
        else:
            self.show_alert_dialog_record_does_not_exist()

    def load_viewed_records(self):
        self.root.ids.total_for_period.text = f"За период с {self.date_list[0]} по {self.date_list[1]}"
        self.root.ids.total_for_period_value_1.text = str(
            len(self.viewed_records_list))
        self.root.ids.total_for_period_value_2.text = str(
            sum(x[3] for x in self.viewed_records_list))
        self.root.ids.total_for_period_value_3.text = str(
            sum(x[4] for x in self.viewed_records_list))
        self.root.ids.total_for_period_value_4.text = str(
            sum(x[5] for x in self.viewed_records_list))

        self.i = 0
        self.switch_viewed_record(0)

    def switch_viewed_record(self, i):
        self.i += i

        self.root.ids.viewing_date.text = self.viewed_records_list[self.i][0]
        self.root.ids.viewing_start.text = str(
            self.viewed_records_list[self.i][1])
        self.root.ids.viewing_stop.text = str(
            self.viewed_records_list[self.i][2])
        self.root.ids.viewing_total.text = str(
            self.viewed_records_list[self.i][3])
        self.root.ids.viewing_fueling_in_liters.text = str(
            self.viewed_records_list[self.i][4])
        self.root.ids.viewing_fueling_in_rubles.text = str(
            self.viewed_records_list[self.i][5])
        self.root.ids.viewing_route.text = self.viewed_records_list[self.i][6]

        if self.i == 0:
            self.root.ids.previous_record.disabled = True
        else:
            self.root.ids.previous_record.disabled = False

        if self.i == len(self.viewed_records_list) - 1:
            self.root.ids.next_record.disabled = True
        else:
            self.root.ids.next_record.disabled = False

    def create_message(self, title, text):
        message = ""

        if self.root.ids.checkbox_viewing_date.active:
            message += f" Дата: {self.root.ids.viewing_date.text}"
        if self.root.ids.checkbox_viewing_start.active:
            message += f" Показания одометра в начале смены: {self.root.ids.viewing_start.text}"
        if self.root.ids.checkbox_viewing_stop.active:
            message += f" Показания одометра в конце смены: {self.root.ids.viewing_stop.text}"
        if self.root.ids.checkbox_viewing_total.active:
            message += f" Пробег за смену: {self.root.ids.viewing_total.text}"
        if self.root.ids.checkbox_viewing_consumed_fuel.active:
            message += f" Израсходовано топлива: {self.root.ids.viewing_consumed_fuel.text}"
        if self.root.ids.checkbox_viewing_fueling_in_liters.active:
            message += f" Заправка в литрах: {self.root.ids.viewing_fueling_in_liters.text}"
        if self.root.ids.checkbox_viewing_fueling_in_rubles.active:
            message += f" Заправка в рублях: {self.root.ids.viewing_fueling_in_rubles.text}"
        if self.root.ids.checkbox_viewing_route.active:
            message += f" Маршрут: {self.root.ids.viewing_route.text}"

        Clipboard.copy(message.strip())

    def load_editing_day(self, data_list):
        self.data_list = list(map(str, data_list))

        (self.root.ids.editing_date.text,
         self.root.ids.editing_start.text,
         self.root.ids.editing_stop.text,
         self.root.ids.editing_total.text,
         self.root.ids.editing_fueling_in_liters.text,
         self.root.ids.editing_fueling_in_rubles.text,
         self.root.ids.editing_route.text) = self.data_list

    def save_editing_day(self, *args):
        with sqlite3.connect("driving_statistics.db") as db:
            cursor = db.cursor()
            cursor.execute(
                """UPDATE my_statistics SET
                start = ?,
                stop = ?,
                total = ?,
                fueling_in_liters = ?,
                fueling_in_rubles = ?,
                route = ?
                WHERE date = ?""",
                (f"{int(self.root.ids.editing_start.text)}",
                 f"{int(self.root.ids.editing_stop.text)}",
                 f"{int(self.root.ids.editing_total.text)}",
                 f"{float(self.root.ids.editing_fueling_in_liters.text)}",
                 f"{float(self.root.ids.editing_fueling_in_rubles.text)}",
                 f"{self.root.ids.editing_route.text}",
                 f"{self.root.ids.editing_date.text}")
            )

        if (self.root.ids.editing_date.text[3:] == datetime.datetime.today().strftime("%d.%m.%Y")[3:] and
            self.root.ids.fuel_card_balance.text != "Не задано..." and
                self.root.ids.editing_fueling_in_rubles.text):

            self.update_fuel_card_balance(
                float(self.day["fuel_card_balance"]) +
                (float(self.data_list[5]) -
                 float(self.root.ids.editing_fueling_in_rubles.text))
            )

        self.root.ids.editing_date.text = ""

    def update_settings_json(self):
        with open("./settings.json", "w") as file:
            json.dump(self.settings, file, indent=4)

    def update_day_json(self):
        with open("./day.json", "w") as file:
            json.dump(self.day, file, indent=4)

    def calculation_and_update_total(self, **kwargs):
        self.day |= kwargs.items()

        if (
            self.day["start"] and
            self.day["stop"] and
            int(self.day["start"]) < int(self.day["stop"])
        ):
            self.day["total"] = str(
                int(self.day["stop"]) - int(self.day["start"]))
            self.root.ids.total.text = self.day["total"]
        else:
            self.day["total"] = "0"
            self.root.ids.total.text = self.day["total"]

        self.update_day_json()

    def calculation_and_update_fuel_consumed(self, num):
        if self.settings["fuel_consumption_per_100_km"] == "Не настроено":
            return "0"
        else:
            if num:
                return str(int(num) * int(self.settings["fuel_consumption_per_100_km"]) / 100)
            else:
                return "0"
        
    def update_fueling(self, id, text):
        if text:
            self.day[id] = str(int(self.day[id]) + int(text))
            self.root.ids[id].text = self.day[id]
            if id == "fueling_in_rubles":
                self.calculation_fuel_card_balance(text)
            self.update_day_json()
        else:
            self.root.ids[id].text = self.day[id]

    def update_route(self, *args):
        self.day["route"] = " ".join(args)
        self.update_day_json()

    def setting_fuel_consumption_per_100_km(self, text):
        if text:
            self.settings["fuel_consumption_per_100_km"] = str(text)
            self.update_settings_json()
        else:
            self.root.ids.fuel_consumption_per_100_km.text = self.settings[
                "fuel_consumption_per_100_km"
            ]

    def setting_work_shift_cost(self, text):
        if text:
            self.settings["work_shift_cost"] = str(text)
            self.root.ids.work_shift_cost.text = self.settings["work_shift_cost"]
            self.update_settings_json()
        else:
            self.root.ids.work_shift_cost.text = self.settings["work_shift_cost"]

    def calculation_salary(self, number_work_shifts):
        if self.settings["work_shift_cost"] == "Не настроено":
            return "0"
        else:
            if number_work_shifts:
                return str(int(self.settings["work_shift_cost"]) * int(number_work_shifts))
            else:
                return "0"

    def calculation_fuel_card_balance(self, last_fueling):
        if self.day["fuel_card_balance"] == "Не задано...":
            pass
        else:
            fuel_card_balance = str(
                float(self.day["fuel_card_balance"]) -
                float(last_fueling)
            )
            self.update_fuel_card_balance(fuel_card_balance)

    def update_fuel_card_balance(self, text):
        if text:
            self.day["fuel_card_balance"] = str(text)
            self.root.ids.fuel_card_balance.text = self.day["fuel_card_balance"]
            self.update_day_json()
        else:
            self.root.ids.fuel_card_balance.text = self.day["fuel_card_balance"]

    def unfocus_route_input(self, text):
        if text:
            if text[-1] == "\n":
                self.root.ids.route.text = text[:-1]
                self.root.ids.route.focus = False

    def show_alert_dialog_record_already_exists(self):
        self.dialog = MDDialog(
            auto_dismiss=False,
            text="""        Запись с текущей датой уже существует.

        Для редактирования сущесвующей записи используйте соответствующий пункт меню.""",
            buttons=[
                MDFlatButton(
                    text="Понятно",
                    on_press=self.close_dialog
                )
            ],
        )
        self.dialog.open()

    def show_alert_dialog_record_does_not_exist(self):
        self.dialog = MDDialog(
            auto_dismiss=False,
            text="""        Запись с выбраной датой не существует.""",
            buttons=[
                MDFlatButton(
                    text="Ясно",
                    on_press=self.close_dialog
                )
            ],
        )
        self.dialog.open()

    def show_dialog_incorrect_date(self):
        self.dialog = MDDialog(
            auto_dismiss=False,
            text="""Укажите дату.""",
            buttons=[
                MDFlatButton(
                    text="Хорошо",
                    on_press=self.close_dialog
                )
            ],
        )
        self.dialog.open()

    def confirmation_start_new_day(self):
        self.dialog = MDDialog(
            auto_dismiss=False,
            text="""        Вы действительно хотите закончить текущую смену и начать новую?

        Внести изменения будет возможно через соответствующий пункт меню.""",
            buttons=[
                MDFlatButton(
                    text="Да",
                    on_press=self.close_dialog,
                    on_release=self.start_new_day
                ),
                MDFlatButton(
                    text="Нет",
                    on_press=self.close_dialog
                )
            ]
        )
        self.dialog.open()

    def confirmation_save_editing_day(self):
        self.dialog = MDDialog(
            auto_dismiss=False,
            text="""        Вы действительно хотите сохранить изменения?""",
            buttons=[
                MDFlatButton(
                    text="Да",
                    on_press=self.close_dialog,
                    on_release=self.save_editing_day
                ),
                MDFlatButton(
                    text="Нет",
                    on_press=self.close_dialog
                )
            ]
        )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def start_new_day(self, *args):
        with sqlite3.connect("driving_statistics.db") as db:
            cursor = db.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS my_statistics (
                                                                    date TEXT PRIMARY KEY,
                                                                    start INT,
                                                                    stop INT,
                                                                    total INT,
                                                                    fueling_in_liters DECIMAL,
                                                                    fueling_in_rubles DECIMAL,
                                                                    route TEXT
                                                                    )
            """)

            try:
                cursor.execute(
                    """INSERT INTO my_statistics
                    (date, start, stop, total, fueling_in_liters, fueling_in_rubles, route) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (f"{self.day['date']}",
                     f"{int(self.day['start'])}",
                     f"{int(self.day['stop'])}",
                     f"{int(self.day['total'])}",
                     f"{float(self.day['fueling_in_liters'])}",
                     f"{float(self.day['fueling_in_rubles'])}",
                     f"{self.day['route']}")
                )

                self.day["date"], self.root.ids.date.text = "Дата", "Дата"
                self.day["start"], self.root.ids.start.text = self.day["stop"], self.day["stop"]
                self.day["stop"], self.root.ids.stop.text = "0", "0"
                self.day["total"], self.root.ids.total.text = "0", "0"
                self.day["fueling_in_liters"], self.root.ids.fueling_in_liters.text = "0", "0"
                self.day["fueling_in_rubles"], self.root.ids.fueling_in_rubles.text = "0", "0"
                self.update_day_json()

            # Такая дата уже существует в базе данных.
            except sqlite3.IntegrityError as e:
                self.show_alert_dialog_record_already_exists()

            except ValueError as e:
                print(e)


if __name__ == "__main__":
    MainApp().run()
