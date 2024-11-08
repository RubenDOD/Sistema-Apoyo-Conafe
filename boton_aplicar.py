import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder

Builder.load_file("boton_aplicar.kv")

class WebViewScreen(BoxLayout):
    def open_form(self, instance):
        webbrowser.open("https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link")

class MyApp(App):
    def build(self):
        return WebViewScreen()

if __name__ == "__main__":
    MyApp().run()
