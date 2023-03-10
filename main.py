import json
import os.path
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker

# Размер окна для запуска на ПК. Перед созданием APK файла, удалить или закомментировать.
from kivy.core.window import Window
Window.size = (1080/3, 2160/3)


class MainApp(MDApp):
    day = {
        "date": "Дата",
        "start": "",
        "stop": "",
        "total": " ",
        "route": "",
        "fuel_consumed": " "
    }
    if not os.path.isfile("./day.json"):
        with open("./day.json", "w") as file:
            json.dump(day, file, indent=4)
    else:
        with open("./day.json", "r") as file:
            day = json.load(file)

    def pick_date(self, *args):
        date = ".".join(reversed(str(args[1]).split("-")))
        self.root.ids.date.text = date
        self.day["date"] = date
        self.update_day_json()

    def show_date_picker(self):
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.pick_date)
        date_picker.open()

    def update_day_json(self):
        # self.day |= kwargs.items()
        with open("./day.json", "w") as file:
            json.dump(self.day, file, indent=4)

    def calculation_total(self, **kwargs):
        self.day |= kwargs.items()

        if self.day["start"] and self.day["stop"] and (int(self.day["start"]) < int(self.day["stop"])):
            self.day["total"] = str(int(self.day["stop"]) - int(self.day["start"]))
            self.root.ids.total.text = self.day["total"]
        else:
            self.day["total"] = " "
            self.root.ids.total.text = self.day["total"]

        self.update_day_json()

    def calculation_fuel_consumed(self):
        pass

    def update_route(self, *args):
        self.day["route"] = " ".join(args)
        self.update_day_json()

    def unfocus_route_input(self, text):
        if text:
            if text[-1] == "\n":
                self.root.ids.route.text = text[:-1]
                self.root.ids.route.focus = False


if __name__ == "__main__":
    MainApp().run()
