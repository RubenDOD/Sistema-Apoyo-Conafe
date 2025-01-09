import kivy
from kivy.app import App
from kivy.graphics import Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from datetime import datetime
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, NumericProperty
import mysql.connector
import json
from datetime import datetime
from kivy.graphics import Color, Rectangle
import pyodbc

# Datos de conexión
server = 'conafe-server.database.windows.net'
database = 'conafe-database'
username = 'admin-conafe'
password = 'MateriaAcaba08/01/25'
driver = '{ODBC Driver 17 for SQL Server}'

class BecaProgresoWindow(BoxLayout):
    # id_educador = NumericProperty(0)
    # id_apoyo = NumericProperty(0)
    def __init__(self, id_educador, id_apoyo,**kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            # Define el color (R, G, B, A)
            Color(0.5, 0.5, 0.5, 1)  # Azul
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # Actualiza el rectángulo cuando el tamaño o posición cambian
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.id_educador = id_educador
        self.id_apoyo = id_apoyo
        print(f"ID del educador: {self.id_educador}")
        print(f"ID del apoyo: {self.id_apoyo}")
        # self.id_educador = 1  # ID del usuario que verá el progreso

        self.conexion = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        self.cursor = self.conexion.cursor()

        self.orientation = 'vertical'

        # Barra de navegación superior
        self.add_widget(self.create_navigation_bar())

        # Título
        self.add_widget(Label(text='Progreso de Beca', size_hint_y=None, height=40))

        # Observaciones
        self.query = """
        SELECT
            observaciones
        FROM apoyo_educador
        WHERE id_apoyo = ? AND id_educador = ?
        """

        self.cursor.execute(self.query, (self.id_apoyo, self.id_educador))
        self.observaciones = self.fetch_as_dict(self.cursor, fetch_one=True)

        observaciones_text = self.observaciones['observaciones'] if self.observaciones and self.observaciones['observaciones'] is not None else 'Sin observaciones'
        self.add_widget(Label(text=observaciones_text, size_hint_y=None, height=40))

        # Contenedor con scroll para el progreso
        scroll_view = ScrollView()
        self.progreso_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        self.progreso_layout.bind(minimum_height=self.progreso_layout.setter('height'))
        scroll_view.add_widget(self.progreso_layout)
        self.add_widget(scroll_view)

        # Cargar datos
        self.cargar_datos()

    def create_navigation_bar(self):
        # Crear el BoxLayout para la barra de navegación
        nav_bar = BoxLayout(size_hint_y=None, height=30)
        with nav_bar.canvas.before:
            # Dibujar el fondo de la barra de navegación
            Color(0.06, 0.45, 0.45, 1)  # Color verde azulado
            self.rect = Rectangle(size=nav_bar.size, pos=nav_bar.pos)

        # Asegurar que el fondo se actualice con el tamaño y posición
        nav_bar.bind(size=self._update_rect, pos=self._update_rect)

        # Agregar un título
        title_label = Label(
            text='Apoyos Económicos Dashboard',
            bold=True,
            size_hint=(0.8, None),
            height=30
        )
        nav_bar.add_widget(title_label)

        # Agregar un botón para regresar
        btn_regresar = Button(
            text='Regresar',
            size_hint=(0.2, None),
            height=30
        )
        btn_regresar.bind(on_release=self.go_back)
        nav_bar.add_widget(btn_regresar)

        return nav_bar
    
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
    
    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def cargar_datos(self):
        # Consulta para obtener los tickets de pago
        query = """
        SELECT 
            tp.mes,
            tp.monto,
            tp.estado,
            tp.fecha_pago
        FROM tickets_pago tp
        WHERE tp.id_educador = ? AND tp.id_apoyo = ?
        ORDER BY 
            CASE tp.mes
                WHEN 'Enero' THEN 1
                WHEN 'Febrero' THEN 2
                WHEN 'Marzo' THEN 3
                WHEN 'Abril' THEN 4
                WHEN 'Mayo' THEN 5
                WHEN 'Junio' THEN 6
                WHEN 'Julio' THEN 7
                WHEN 'Agosto' THEN 8
                WHEN 'Septiembre' THEN 9
                WHEN 'Octubre' THEN 10
                WHEN 'Noviembre' THEN 11
                WHEN 'Diciembre' THEN 12
            END ASC
        """
        self.cursor.execute(query, (self.id_educador, self.id_apoyo))
        tickets = self.fetch_as_dict(self.cursor, fetch_one=False)

        if not tickets:
            self.progreso_layout.add_widget(Label(text="No se han generado tickets para este apoyo.", size_hint_y=None, height=40))
            return

        # Mostrar los tickets en un formato de lista
        self.progreso_layout.add_widget(Label(text="Tickets de Pago:", size_hint_y=None, height=40))

        for ticket in tickets:
            # Crear un layout horizontal para mostrar cada ticket
            ticket_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

            # Mes del ticket
            ticket_layout.add_widget(Label(text=f"Mes: {ticket['mes']}", size_hint_x=0.3))

            # Monto del ticket
            ticket_layout.add_widget(Label(text=f"Monto: ${ticket['monto']:.2f}", size_hint_x=0.2))

            # Estado del ticket
            estado = ticket['estado']
            estado_label = Label(text=f"Estado: {estado}", size_hint_x=0.3)
            if estado == "Pagado":
                estado_label.color = (0, 1, 0, 1)  # Verde
            elif estado == "Pendiente":
                estado_label.color = (1, 1, 0, 1)  # Amarillo
            elif estado == "Cancelado":
                estado_label.color = (1, 0, 0, 1)  # Rojo
            ticket_layout.add_widget(estado_label)

            # Fecha de pago (si el estado es pagado)
            if estado == "Pagado":
                ticket_layout.add_widget(Label(text=f"Pagado el: {ticket['fecha_pago']}", size_hint_x=0.4))
            else:
                ticket_layout.add_widget(Label(text="", size_hint_x=0.4))

            # Agregar el layout del ticket a la vista
            self.progreso_layout.add_widget(ticket_layout)

    def cerrar_app(self, instance):
        self.stop()

    def on_stop(self):
        self.cursor.close()
        self.conexion.close()
    
    def go_back(self, instance):
        App.get_running_app().root.current = 'apoyos_economicos'

    

class BecaProgresoApp(App):
    def build(self):
        return BecaProgresoWindow()

if __name__ == '__main__':
    # Supongamos que estamos viendo el progreso para el usuario con ID 1
    BecaProgresoApp().run() 