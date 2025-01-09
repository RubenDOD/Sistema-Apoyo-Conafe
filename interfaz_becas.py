# main.py
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
import mysql.connector
import json
from datetime import datetime
from kivy.graphics import Color, Ellipse, Rectangle
from progreso_apoyos import BecaProgresoWindow

import pyodbc

# Datos de conexión
server = 'conafe-server.database.windows.net'
database = 'conafe-database'
username = 'admin-conafe'
password = 'MateriaAcaba08/01/25'
driver = '{ODBC Driver 17 for SQL Server}'


class BecasWindow(BoxLayout):

    def __init__(self, id_educador, **kwargs):
        super().__init__(**kwargs)
        self.id_educador = id_educador
    
        # Barra de navegación superior
        #self.add_widget(self.create_navigation_bar())

        # Hacemos la consulta de las becas del educador
        self.obtener_becas()

    def fetch_as_dict(self, cursor, fetch_one=False):
        """
        Convierte los resultados de una consulta de cursor en un diccionario o lista de diccionarios.

        Args:
            cursor: El cursor ejecutado de la consulta SQL.
            fetch_one (bool): Si es True, usa fetchone; si es False, usa fetchall.

        Returns:
            dict o list[dict]: Diccionario si fetch_one es True, lista de diccionarios si es False.
        """
        columns = [column[0] for column in cursor.description]
        if fetch_one:
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
        else:
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def obtener_becas(self):
        # Limpiar cualquier widget previo
        self.ids.becas_layout.clear_widgets()
        
        # Establecer conexión a la base de datos
        self.conexion = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        self.cursor = self.conexion.cursor()

        # Consulta para obtener las becas del educador
        query = """
        SELECT ae.id_apoyo, aeco.tipo_apoyo, ae.estado_apoyo 
        FROM apoyo_educador ae
        JOIN apoyo_economico aeco ON ae.id_apoyo = aeco.id_apoyo
        WHERE ae.id_educador = ?
        """
        self.cursor.execute(query, (self.id_educador,))
        becas = self.fetch_as_dict(self.cursor, fetch_one=False)

        print("Becas del educador:", becas)
        # Crear botones para cada beca
        for beca in becas:
            btn = Button(
                text=f"{beca['tipo_apoyo']} - {beca['estado_apoyo']}", 
                size_hint_y=None, 
                height=50,
            )
            # Pasar id_apoyo como parámetro al presionar
            btn.bind(on_press=lambda instance, id_apoyo=beca['id_apoyo']: 
                     self.ver_detalles_apoyo(id_apoyo))
            self.ids.becas_layout.add_widget(btn)

        self.cursor.close()
        self.conexion.close()

    def mostrar_detalle_beca(self, id_apoyo):
        # Navegar a la pantalla de detalle de beca
        detalle_screen = self.manager.get_screen('detalle_beca')
        detalle_screen.id_apoyo = id_apoyo
        detalle_screen.id_educador = self.id_educador
        self.manager.current = 'detalle_beca'

    def go_back(self, instance):
        App.get_running_app().root.current = 'lec'

    def ver_detalles_apoyo(self, id_apoyo): 
        print("Ver detalles del apoyo.")
        app = App.get_running_app()

        # Crear una instancia de ApoyosWindow
        progreso_apoyo_window = BecaProgresoWindow(id_educador = self.id_educador, id_apoyo = id_apoyo)
        progreso_apoyo_screen = app.root.get_screen('progreso_apoyo')
        progreso_apoyo_screen.clear_widgets()
        progreso_apoyo_screen.add_widget(progreso_apoyo_window)

        # Cambia a la pantalla de apoyos
        app.root.current = 'progreso_apoyo'

class BecasApp(App):
    def build(self):
        return BecasWindow()



if __name__ == '__main__':
    BecasApp().run()