from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable_convocatoriasUser import DataTableConvUser
from datetime import datetime
import hashlib
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from db_connection import execute_query


class aplicarAspiranteWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("aplicarAspirante.kv")  # Carga explícita de admin.kv

        content = self.ids.scrn_contents
        users = self.get_users("General", 0)
        userstable = DataTableConvUser(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'aspirante'  # Cambia a la pantalla 'aspirante'

    def reload_users(self):
        # Obtiene el contenedor de usuarios
        content = self.ids.scrn_contents
        content.clear_widgets()

        # Obtiene nuevamente la lista de usuarios
        users = self.get_users("General", 0)

        # Crea la tabla actualizada y agrégala a la pantalla
        userstable = DataTableConvUser(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, idx):
        if button_text == 'Ver':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.abrir_documento(conv_id)
        elif button_text == 'Aplicar':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.abrir_forms(conv_id)

    def abrir_documento(self, conv_id):
        # Consulta la URL del documento
        sql = "SELECT url_convocatoria FROM ConvocatoriaActual WHERE id_Convo = ?"
        url = execute_query(sql, (conv_id,))

        # Abre la URL en el navegador
        if url:
            webbrowser.open(url[0][0])  # Abre la URL en el navegador
            print(f"Convocatoria {conv_id} abierta con éxito.")
        else:
            print(f"No se encontró la convocatoria con ID {conv_id}.")

    def abrir_forms(self, conv_id):
        # Consulta la URL del formulario
        sql = "SELECT url_forms FROM ConvocatoriaActual WHERE id_Convo = ?"
        url = execute_query(sql, (conv_id,))

        # Abre la URL en el navegador
        if url:
            webbrowser.open(url[0][0])  # Abre la URL en el navegador
            print(f"Formulario {conv_id} abierto con éxito.")
        else:
            print(f"No se encontró el formulario con ID {conv_id}.")

    def get_users(self, mode, id):
        if mode == "General":
            _convocatorias = OrderedDict()
            _convocatorias['ID'] = {}
            _convocatorias['nombre'] = {}
            _convocatorias['status'] = {}

            sql = "SELECT * FROM ConvocatoriaActual WHERE estado_convocatoria = 'Abierta'"
            users = execute_query(sql)

            ids = [user[0] for user in users]
            nombres = [user[1] for user in users]
            status = [user[4] for user in users]

            for idx, _ in enumerate(users):
                _convocatorias['ID'][idx] = ids[idx]
                _convocatorias['nombre'][idx] = nombres[idx]
                _convocatorias['status'][idx] = status[idx]

            return _convocatorias

    def change_screen(self, instance):
        if instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'

class aplicarAspiranteApp(App):
    def build(self):
        return aplicarAspiranteWindow()

if __name__ == '__main__':
    aplicarAspiranteApp().run()
