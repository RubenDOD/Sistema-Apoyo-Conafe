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
from db_connection import execute_query

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
        """Solicita un apoyo para el educador si aún no lo tiene."""
        # Verificar si el usuario ya tiene un apoyo
        query = "SELECT * FROM apoyo_educador WHERE id_educador = %s"
        resultado = execute_query(query, (self.id_educador,))

        print("Apoyos con los que ya cuenta el usuario:", resultado)

        # Verificar si el usuario ya tiene el apoyo solicitado
        for result in resultado:
            if result['id_apoyo'] == apoyo['id_apoyo']:
                # Mostrar mensaje de error si el apoyo ya existe
                popup = Popup(
                    title='Error',
                    content=Label(text='Ya cuentas con este apoyo.'),
                    size_hint=(0.6, 0.4)
                )
                popup.open()
                return

        # Insertar el nuevo apoyo para el usuario
        insert_query = """
            INSERT INTO apoyo_educador (id_apoyo, id_educador, estado_apoyo)
            VALUES (%s, %s, 'pendiente')
        """
        execute_query(insert_query, (apoyo['id_apoyo'], self.id_educador))

        # Mostrar mensaje de éxito
        popup = Popup(
            title='Éxito',
            content=Label(text='Has solicitado el apoyo exitosamente.'),
            size_hint=(0.6, 0.4)
        )
        popup.open()

    def go_back(self, instance):
        App.get_running_app().root.current = 'lec'

class ApoyoApp(App):
    def build(self):
        return SolicitarApoyoWindow()

if __name__ == '__main__':
    ApoyoApp().run()