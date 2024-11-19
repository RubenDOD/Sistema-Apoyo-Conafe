from collections import OrderedDict
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
import mysql.connector

# Establecer el fondo de la ventana en blanco
Window.clearcolor = (1, 1, 1, 1)  # Valores RGBA (1,1,1,1) es blanco puro

class CircleWidget(Widget):
    def __init__(self, is_active=False, color=(0.5, 0.5, 0.5, 1),**kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.is_active = is_active
        self.bind(pos=self.update_circle, size=self.update_circle)
        self.draw_circle()

    def draw_circle(self, *args):
        self.canvas.clear()
        with self.canvas:
            if self.is_active:
                Color(*self.color)  # Azul
            else:
                Color(0.5, 0.5, 0.5, 1)  # Gris
            diameter = min(self.width, self.height) * 0.8
            Ellipse(size=(diameter, diameter), pos=(self.center_x - diameter / 2, self.center_y - diameter / 2))

    def update_circle(self, *args):
        self.draw_circle()

class AspiranteSeguimientoScreen(BoxLayout):
    def __init__(self, id_aspirante = None,**kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.id_aspirante = 2
        # Barra de navegación superior
        self.add_widget(self.create_navigation_bar())

        # Db_config
        self.db_config = {
            'host':'localhost',
            'user':'root',
            'passwd':'1234',
            'database':'CONAFE'
        }

        # Obtenemos la información del aspirante
        info_aspirante = self.consultar_observaciones(self.id_aspirante, self.db_config)

        # Nombre del aspirante
        nombre_aspirante = Label(
            text="Nombre: " + str(info_aspirante['nombres']) + " " + str(info_aspirante['apellidoPaterno']) + " " + str(info_aspirante['apellidoMaterno']),
            size_hint=(1, 0.1),
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1)  # Texto en negro
        )
        nombre_aspirante.bind(size=nombre_aspirante.setter('text_size'))
        self.add_widget(nombre_aspirante)

        # Capacitador
        capacitador_label = Label(
            text="Número de capacitador: " +  str(info_aspirante['id_Capacitador']) + " Correo: " + str(info_aspirante['correo_Capacitador']),
            size_hint=(1, 0.1),
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1)  # Texto en negro
        )
        capacitador_label.bind(size=capacitador_label.setter('text_size'))
        self.add_widget(capacitador_label)

        # Estado de la capacitación
        estado_label = Label(
            text="Estado de capacitación: " + str(info_aspirante['estadoCapacitacion']),
            size_hint=(1, 0.1),
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1)  # Texto en negro
        )
        estado_label.bind(size=estado_label.setter('text_size'))
        self.add_widget(estado_label)

        # Label para mostrar las observaciones
        self.observations_label = Label(
            text="Observaciones: " + str(info_aspirante['observaciones']),
            size_hint=(1, 0.1),
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1)  # Texto en negro
        )
        self.observations_label.bind(size=self.observations_label.setter('text_size'))
        self.add_widget(self.observations_label)

        # Estados de capacitación
        self.states = ["En Inicio", "Cursos intermedios", "Finalizando Cursos", "Finalizado"]
        # Buscamos el estado del aspirante en la base de datos
        print("Estado actual: " + str(info_aspirante['estadoCapacitacion']))
        self.current_state = self.states.index(str(info_aspirante['estadoCapacitacion'])) if str(info_aspirante['estadoCapacitacion']) in self.states else print("Estado no reconocido")

        self.states_layout = GridLayout(cols=4, size_hint=(1, 0.2))

        for i, state in enumerate(self.states):
            circle_layout = BoxLayout(orientation='vertical')

            # Elegimos un color distinto si el estado actual es Rechazado o Congelado
            if str(info_aspirante['estadoCapacitacion']) == "Rechazado":
                print("Es rechazado")
                color = (1, 0, 0, 1)  # Rojo
                is_active = True
            elif str(info_aspirante['estadoCapacitacion']) == "Congelado":
                print("Es congelado")
                color = (1, 1, 0, 1)  # Amarillo
                is_active = True
            else:
                print("No es rechazado ni congelado")
                color = (0, 0, 1, 1) # Azul
                is_active = (i <= self.current_state)

            # Crear el widget del círculo
            circle_widget = CircleWidget(is_active=is_active, color=color, size_hint=(1, 0.7))
            circle_layout.add_widget(circle_widget)

            # Etiqueta del estado
            label = Label(
                text=state,
                size_hint=(1, 0.3),
                halign="center",
                valign="middle",
                color=(0, 0, 0, 1)  # Texto en negro
            )
            label.bind(size=label.setter('text_size'))
            circle_layout.add_widget(label)

            self.states_layout.add_widget(circle_layout)

        self.add_widget(self.states_layout)


    def consultar_observaciones(self, id_aspirante, db_config=None):
        try:
            with mysql.connector.connect(**db_config) as mydb:
                with mydb.cursor() as my_cursor:
                    # Consulta optimizada
                    sql = """
                        SELECT 
                            ca.id_Capacitador,
                            a.nombres AS nombre_aspirante,
                            ca.fechaInicio,
                            ca.fechaFinalizacion,
                            ca.observaciones,
                            ca.estadoCapacitacion,
                            a.apellidoPaterno AS apellido_paterno,
                            a.apellidoMaterno AS apellido_materno,
                            u.correo
                        FROM 
                            CapacitadorAspirante ca
                        JOIN 
                            Aspirante a ON ca.id_Aspirante = a.id_Aspirante
                        JOIN 
                            Usuario u ON ca.id_Capacitador = u.id_Usuario
                        WHERE 
                            ca.id_Aspirante = %s
                    """
                    my_cursor.execute(sql, (id_aspirante,))
                    info_aspirante = my_cursor.fetchone()

                    # Validar si hay resultados
                    if not info_aspirante:
                        raise ValueError("No se encontraron datos para el aspirante.")

                    # Construir el diccionario
                    _datosAspirante = {
                        'id_Capacitador': info_aspirante[0],
                        'nombres': info_aspirante[1],
                        'fechaInicio': info_aspirante[2],
                        'fechaFinalizacion': info_aspirante[3],
                        'observaciones': info_aspirante[4],
                        'estadoCapacitacion': info_aspirante[5],
                        'apellidoPaterno': info_aspirante[6],
                        'apellidoMaterno': info_aspirante[7],
                        'correo_Capacitador': info_aspirante[8]
                    }

                    return _datosAspirante
        except mysql.connector.Error as err:
            print(f"Error al conectar con la base de datos: {err}")
            return None

    def create_navigation_bar(self):
        # Crear la barra de navegación superior
        nav_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=30
        )

        with nav_bar.canvas.before:
            Color(0.06, 0.45, 0.45, 1)  # Color de fondo de la barra
            self.nav_rect = Rectangle(size=nav_bar.size, pos=nav_bar.pos)
        nav_bar.bind(size=self._update_nav_bg, pos=self._update_nav_bg)


        # Etiqueta central
        title_label = Label(
            text='Capacitador Dashboard',
            bold=True,
            halign='center',
            size_hint=(0.8, None),
            height=30,
            color=(1, 1, 1, 1)  # Texto en blanco
        )
        title_label.bind(size=title_label.setter('text_size'))
        nav_bar.add_widget(title_label)

        # Botón de "Regresar"
        back_button = Button(
            text='Regresar',
            size_hint=(0.1, None),
            height=30
        )
        back_button.bind(on_release=self.go_back)
        nav_bar.add_widget(back_button)

        return nav_bar

    def _update_nav_bg(self, instance, value):
        # Actualiza el fondo de la barra de navegación al cambiar tamaño o posición
        self.nav_rect.size = instance.size
        self.nav_rect.pos = instance.pos

    def go_back(self, instance):
        # Volvemos a la Screen principal del aspirante
        App.get_running_app().root.current = 'aspirante'

class ObservationsApp(App):
    def build(self):
        return AspiranteSeguimientoScreen()

if __name__ == "__main__":
    ObservationsApp().run()