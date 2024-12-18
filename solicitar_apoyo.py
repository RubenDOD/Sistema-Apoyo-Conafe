import kivy
from kivy.app import App
from kivy.graphics import Line

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle


import mysql.connector



class SolicitarApoyoWindow(BoxLayout):
    def __init__(self, id_educador,**kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            # Define el color (R, G, B, A)
            Color(0.5, 0.5, 0.5, 1)  # Azul
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # Actualiza el rectángulo cuando el tamaño o posición cambian
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.id_educador = id_educador  # ID de usuario predeterminado
        self.conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='CONAFE'
        )
        self.cursor = self.conexion.cursor(dictionary=True)

        self.orientation = 'vertical'

        # Barra de navegación superior
        self.add_widget(self.create_navigation_bar())

        # Título
        self.add_widget(Label(text='Lista de Apoyos Disponibles', size_hint_y=None, height=40))

        # Contenedor con scroll
        scroll_view = ScrollView()
        grid = GridLayout(cols=4, size_hint_y=None, row_default_height=40, spacing=5)
        grid.bind(minimum_height=grid.setter('height'))

        # Encabezados de tabla
        grid.add_widget(Label(text='Clave Apoyo', bold=True))
        grid.add_widget(Label(text='Monto', bold=True))
        grid.add_widget(Label(text='Información Detallada', bold=True))
        grid.add_widget(Label(text='Solicitar Apoyo', bold=True))

        # Obtener datos de 'apoyo_economico'
        self.cursor.execute("SELECT * FROM apoyo_economico")
        apoyos = self.cursor.fetchall()

        for apoyo in apoyos:
            grid.add_widget(Label(text=apoyo['claveApoyo']))
            grid.add_widget(Label(text=str(apoyo['monto_apoyo'])))
            btn_info = Button(text='Ver Detalles', size_hint_y=None, height=40)
            btn_info.bind(on_release=lambda btn, a=apoyo: self.mostrar_detalles(a))
            grid.add_widget(btn_info)
            btn_solicitar = Button(text='Solicitar', size_hint_y=None, height=40)
            btn_solicitar.bind(on_release=lambda btn, a=apoyo: self.solicitar_apoyo(a))
            grid.add_widget(btn_solicitar)

        scroll_view.add_widget(grid)
        self.add_widget(scroll_view)

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

    def mostrar_detalles(self, apoyo):
        contenido = BoxLayout(orientation='vertical', spacing=10, padding=10)
        contenido.add_widget(Label(text=f"Nombre de Apoyo: {apoyo['tipo_apoyo']}"))
        contenido.add_widget(Label(text=f"Monto: {apoyo['monto_apoyo']}"))
        contenido.add_widget(Label(text=f"Fecha Inicio (Primer Pago): Se establecerá una fecha cuando la solicitud sea aprobada."))
        contenido.add_widget(Label(text=f"Periodo de Entrega (meses): Durante {apoyo['periodo_entrega_meses']} meses"))

        btn_cerrar = Button(text='Cerrar', size_hint_y=None, height=40)
        contenido.add_widget(btn_cerrar)

        popup = Popup(title='Detalles del Apoyo', content=contenido, size_hint=(0.8, 0.8))
        btn_cerrar.bind(on_release=popup.dismiss)
        popup.open()

    def solicitar_apoyo(self, apoyo):
        # Verificar si el usuario ya tiene un apoyo
        query = "SELECT * FROM apoyo_educador WHERE id_educador = %s"
        self.cursor.execute(query, (self.id_educador,))
        resultado = self.cursor.fetchall()

        print("Apoyos con los que ya cuenta el usuario:", resultado)

        tiene_beca = False
        for result in resultado:
            id_apoyo_resultado = result['id_apoyo']

            # Verificar si el usuario ya el apoyo solicitado
            if id_apoyo_resultado == apoyo['id_apoyo']:
                # El usuario ya tiene un apoyo
                popup = Popup(title='Error',
                            content=Label(text='Ya cuentas con este apoyo.'),
                            size_hint=(0.6, 0.4))
                popup.open()
                tiene_beca = True
                break

        if not tiene_beca:
            # Insertar el nuevo apoyo para el usuario
            insert_query = "INSERT INTO apoyo_educador (id_apoyo, id_educador, estado_apoyo) VALUES (%s, %s, 'pendiente')"
            self.cursor.execute(insert_query, (apoyo['id_apoyo'], self.id_educador))
            self.conexion.commit()

            popup = Popup(title='Éxito',
                    content=Label(text='Has solicitado el apoyo exitosamente.'),
                    size_hint=(0.6, 0.4))
            popup.open()

    def on_stop(self):
        self.cursor.close()
        self.conexion.close()
        
    def go_back(self, instance):
        App.get_running_app().root.current = 'lec'

class ApoyoApp(App):
    def build(self):
        return SolicitarApoyoWindow()

if __name__ == '__main__':
    ApoyoApp().run()