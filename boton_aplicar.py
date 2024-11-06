import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class WebViewScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Encabezado
        header = Label(text="Formulario de Google", size_hint_y=0.1, font_size=24)
        self.add_widget(header)

        # Botón para abrir el formulario en el navegador
        open_button = Button(text="Abrir Formulario", size_hint_y=0.2)
        open_button.bind(on_release=self.open_form)
        self.add_widget(open_button)

    def open_form(self, instance):
        webbrowser.open("https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link")


class MyApp(App):
    def build(self):
        return WebViewScreen()


if __name__ == "__main__":
    MyApp().run()
