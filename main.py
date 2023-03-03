from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout

from kivy.core.window import Window
Window.size = (1080/3, 2160/3)  # Дя тестов...


class LastEntry(BoxLayout):
    pass


class MainApp(MDApp):

    def build(self):
        return LastEntry()


if __name__ == "__main__":
    MainApp().run()
