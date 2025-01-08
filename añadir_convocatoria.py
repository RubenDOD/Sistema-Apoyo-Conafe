from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from db_connection import execute_query
from db_connection import execute_non_query
import validators
import requests

# Carga explícita del archivo .kv
Builder.load_file("añadir_convocatoria.kv")

class AddConvoScreen(Screen):
    # Inicializar variables para almacenar las URLs
    url_documento = None
    url_forms = None

    # Recibe la referencia de ConvocatoriaWindow para recargar los datos al agregar una nueva convocatoria
    def __init__(self, convocatoria_window=None, **kwargs):
        super().__init__(**kwargs)
        self.convocatoria_window = convocatoria_window  # Guarda la referencia para recargar la interfaz

    def mostrar_popup_url(self, type):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        if type == 'Documento':
            url_input = TextInput(hint_text="Ingresa la URL del documento de la convocatoria", multiline=False)
            content.add_widget(url_input)
        else:
            url_input = TextInput(hint_text="Ingresa la URL del forms de la convocatoria", multiline=False)
            content.add_widget(url_input)

        boton_aceptar = Button(text="Aceptar", size_hint_y=None, height=40)
        content.add_widget(boton_aceptar)

        popup = Popup(title="Referencia de la convocatoria",
                      content=content,
                      size_hint=(0.8, 0.4))

        def aceptar_url(instance):
            url = url_input.text
            if not self.validar_url(url):
                self.mostrar_popup_error("URL no válida. Por favor, ingrese una URL válida.")
                return

            if type == 'Documento':
                self.url_documento = url
            else:
                self.url_forms = url
            print(f"URL ingresada para {type}: {url}")
            popup.dismiss()

        boton_aceptar.bind(on_press=aceptar_url)
        popup.open()

    def validar_url(self, url):
        # Verificar si la URL tiene un formato correcto
        if not validators.url(url):
            return False

        # Configurar cabeceras para simular un navegador
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }

        # Verificar si la URL responde correctamente usando GET y con User-Agent
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def seleccionar_archivo_pdf(self):
        root = Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)

        archivo_seleccionado = askopenfilename(
            title="Seleccionar Archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        if archivo_seleccionado:
            print(f"Archivo seleccionado: {archivo_seleccionado}")
            self.mostrar_popup_confirmacion(archivo_seleccionado)

    def mostrar_popup_confirmacion(self, archivo_nombre):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label_confirmacion = Label(text=f"Archivo seleccionado: {archivo_nombre}")
        content.add_widget(label_confirmacion)

        boton_aceptar = Button(text="Aceptar", size_hint_y=None, height=40)
        content.add_widget(boton_aceptar)

        popup = Popup(title="Confirmación de Archivo",
                      content=content,
                      size_hint=(0.8, 0.4))

        boton_aceptar.bind(on_press=popup.dismiss)
        popup.open()

    def agregar_convocatoria(self):
        # Verificar que los campos no estén vacíos
        nombre_convocatoria = self.ids.nombre_convocatoria.text

        # Verificar si el nombre de la convocatoria y alguna URL están completos
        if not nombre_convocatoria or not (self.url_documento or self.url_forms):
            self.mostrar_popup_error("Datos incompletos: ingrese el nombre y al menos una URL.")
        else:
            try:
                # Inserta la convocatoria con el estado "Cerrada"
                sql = """
                    INSERT INTO ConvocatoriaActual (nombre_convocatoria, url_convocatoria, url_forms, estado_convocatoria)
                    VALUES (?, ?, ?, ?)
                """
                data = (nombre_convocatoria, self.url_documento, self.url_forms, 'Cerrada')

                execute_non_query(sql, data)

                print("Convocatoria añadida con éxito.")
                print("Datos:", nombre_convocatoria, self.url_documento, self.url_forms, "Cerrada")

                # Llama a reload_users para actualizar la interfaz en ConvocatoriaWindow
                if self.convocatoria_window:
                    self.convocatoria_window.reload_users()

                # Cambiar de vuelta a ConvocatoriaWindow después de agregar
                App.get_running_app().root.current = 'convocatorias'  # Cambia a la pantalla de convocatorias

            except Exception as err:
                self.mostrar_popup_error(f"Error al conectar con la base de datos: {err}")

    def mostrar_popup_error(self, mensaje):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label_error = Label(text=mensaje)
        content.add_widget(label_error)

        boton_aceptar = Button(text="Aceptar", size_hint_y=None, height=40)
        content.add_widget(boton_aceptar)

        popup = Popup(title="Error",
                      content=content,
                      size_hint=(0.8, 0.4))

        boton_aceptar.bind(on_press=popup.dismiss)
        popup.open()

class AddConvoApp(App):  # Aplicación principal para pruebas
    def build(self):
        return AddConvoScreen()

if __name__ == '__main__':
    AddConvoApp().run()
