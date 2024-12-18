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

        self.conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='conafe'
        )
        self.cursor = self.conexion.cursor(dictionary=True)

        self.orientation = 'vertical'

        # Barra de navegación superior
        self.add_widget(self.create_navigation_bar())

        # Título
        self.add_widget(Label(text='Progreso de Beca', size_hint_y=None, height=40))

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
    
    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def cargar_datos(self):
        # Consulta para obtener la información del apoyo
        query = """
        SELECT 
            ae.estado_apoyo,
            ae.numero_cuenta,
            aeco.tipo_apoyo,
            aeco.monto_apoyo,
            aeco.fecha_inicio,
            aeco.periodo_entrega_meses,
            aeco.meses_entrega
        FROM apoyo_educador ae
        JOIN apoyo_economico aeco ON ae.id_apoyo = aeco.id_apoyo
        WHERE ae.id_educador = %s AND ae.estado_apoyo = 'Aceptado'
        AND ae.id_apoyo = %s
        """
        self.cursor.execute(query, (self.id_educador, self.id_apoyo,))
        apoyo = self.cursor.fetchone()
        print(f"Apoyo obtenido: {apoyo}")   
        if not apoyo:
            self.progreso_layout.add_widget(Label(text="El apoyo aún no es aceptado por el departamento de apoyos.", size_hint_y=None, height=40))
            return

        # Mostrar información del apoyo
        self.progreso_layout.add_widget(Label(text=f"Tipo de Apoyo: {apoyo['tipo_apoyo']}", size_hint_y=None, height=30))
        self.progreso_layout.add_widget(Label(text=f"Monto Mensual: ${apoyo['monto_apoyo']}", size_hint_y=None, height=30))
        self.progreso_layout.add_widget(Label(text=f"Monto total: {apoyo['periodo_entrega_meses'] * apoyo['monto_apoyo']}", size_hint_y=None, height=30))
        self.progreso_layout.add_widget(Label(text=f"Fecha de Inicio: {apoyo['fecha_inicio']}", size_hint_y=None, height=30))
        self.progreso_layout.add_widget(Label(text=f"Periodo de Entrega: {apoyo['periodo_entrega_meses']} meses", size_hint_y=None, height=30))
        self.progreso_layout.add_widget(Label(text=f"Número de Cuenta: {apoyo['numero_cuenta']}", size_hint_y=None, height=30))

        # Calcular progreso
        try:
            meses_entrega = json.loads(apoyo['meses_entrega'])
        except (TypeError, json.JSONDecodeError):
            meses_entrega = []

        total_meses = apoyo['periodo_entrega_meses']

        meses_map = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }

        # Obtener el mes actual
        mes_actual = datetime.now().month
        print(f"Mes actual (número): {mes_actual}")

        # Convertir los nombres a números y filtrar los meses pagados
        meses_pagados = [mes for mes in meses_entrega if meses_map[mes.lower()] <= mes_actual]

        meses_pagados_len = len(meses_pagados)
        progreso = (meses_pagados_len / total_meses) * 100 if total_meses > 0 else 0

        # Mostrar barra de progreso
        self.progreso_layout.add_widget(Label(text="Progreso de Pagos:", size_hint_y=None, height=80))
        progress_bar = ProgressBar(value=progreso, max=100, size_hint_y=None, height=200)
        self.progreso_layout.add_widget(progress_bar)

        # Mostrar detalles de pagos realizados
        for mes in meses_pagados:
            # Crear un layout horizontal para el texto y la imagen
            mes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=-5)

            # Etiqueta con el nombre del mes
            mes_label = Label(
                text=f"Pago realizado en: {mes}",
                size_hint_x=0.5,  # Deja menos espacio horizontal para el texto
                halign="center",  # Alinea el texto a la izquierda
                valign="middle"  # Alinea verticalmente en el centro
            )
            mes_label.bind(size=mes_label.setter('text_size'))  # Ajusta el tamaño del texto al contenedor

            # Imagen de palomita
            check_icon = Image(
                source='check.png',
                size_hint_x= 0.5,  # Deshabilita la proporción horizontal automática
                size_hint_y= None,  # Deshabilita la proporción vertical automática
                height=25,  # Tamaño más pequeño
                width=1  # Tamaño más pequeño
            )

            # Agregar el texto y la imagen al layout
            mes_layout.add_widget(mes_label)
            mes_layout.add_widget(check_icon)

            # Agregar el layout al progreso_layout
            self.progreso_layout.add_widget(mes_layout)

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