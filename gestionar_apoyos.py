import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
import re
from db_connection import execute_query
from db_connection import execute_non_query

class ApoyosSolicitadosWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            # Define el color (R, G, B, A)
            Color(0.5, 0.5, 0.5, 1)  # Azul
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # Actualiza el rectángulo cuando el tamaño o posición cambian
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.orientation = 'vertical'

        # Barra de navegación superior
        self.add_widget(self.create_navigation_bar())

        # Título
        self.add_widget(Label(text='Apoyos Solicitados', size_hint_y=None, height=40))

        # Contenedor con scroll
        self.scroll_view = ScrollView()
        self.add_widget(self.scroll_view)

        # Crear el grid de apoyos
        self.crear_grid_apoyos()

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

    def crear_grid_apoyos(self):
        # Limpiar el contenido anterior del scroll_view
        self.scroll_view.clear_widgets()

        grid = GridLayout(cols=5, size_hint_y=None, row_default_height=40, spacing=5)
        grid.bind(minimum_height=grid.setter('height'))

        # Encabezados de tabla
        grid.add_widget(Label(text='ID Apoyo', bold=True))
        grid.add_widget(Label(text='Clave del Apoyo', bold=True))
        grid.add_widget(Label(text='Aspirante', bold=True))
        grid.add_widget(Label(text='Estado Actual', bold=True))
        grid.add_widget(Label(text='Cambiar Estado', bold=True))

        # Obtener datos de las tablas
        query = """
        SELECT 
            ae.id_apoyo,
            aeco.tipo_apoyo,
            aeco.claveApoyo,
            u.correo AS aspirante_correo,
            u.id_Usuario AS id_educador,
            ae.estado_apoyo
        FROM apoyo_educador ae
        JOIN apoyo_economico aeco ON ae.id_apoyo = aeco.id_apoyo
        JOIN Usuario u ON ae.id_educador = u.id_Usuario
        """
        apoyos = execute_query(query)

        # Lista de estados posibles
        estados = ['Aceptado', 'Rechazado', 'Congelado']

        for apoyo in apoyos:
            grid.add_widget(Label(text=str(apoyo['id_apoyo'])))
            grid.add_widget(Label(text=apoyo['claveApoyo']))

            # Botón "Ver" para mostrar información del aspirante
            btn_ver_aspirante = Button(text='Ver', size_hint_y=None, height=40)
            # Capturar el apoyo actual en el lambda para evitar problemas de alcance
            btn_ver_aspirante.bind(on_release=lambda btn, a=apoyo: self.ver_informacion_aspirante(a))
            grid.add_widget(btn_ver_aspirante)

            grid.add_widget(Label(text=apoyo['estado_apoyo']))

            spinner = Spinner(
                text='Seleccionar',
                values=estados,
                size_hint_y=None,
                height=40
            )
            spinner.bind(text=lambda spinner, text, a=apoyo: self.mostrar_popup_observaciones(a, text))
            grid.add_widget(spinner)

        self.scroll_view.add_widget(grid)

    def ver_informacion_aspirante(self, apoyo):
        id_educador = apoyo['id_educador']
        # Obtener información completa del aspirante
        query = """
        SELECT
            u.id_Usuario,
            u.correo,
            u.acceso,
            aspirante.nombres,
            aspirante.apellidoPaterno,
            aspirante.apellidoMaterno,
            maestro.estadoSalud,
            maestro.genero,
            maestro.edad,
            maestro.capacidadDiferente
        FROM Usuario u 
        JOIN LEC maestro ON u.id_Usuario = maestro.id_Usuario
        JOIN Aspirante ON maestro.id_Usuario = Aspirante.id_Aspirante
        WHERE u.id_Usuario = %s
        """
        aspirante = execute_query(query, (id_educador,))

        if aspirante:
            contenido = BoxLayout(orientation='vertical', spacing=10, padding=10)
            contenido.add_widget(Label(text=f"Correo: {aspirante['correo']}"))
            contenido.add_widget(Label(text=f"Rol: {aspirante['acceso']}"))
            contenido.add_widget(Label(text=f"Nombre: {aspirante['nombres']}"))
            contenido.add_widget(Label(text=f"Apellido Paterno: {aspirante['apellidoPaterno']}"))
            contenido.add_widget(Label(text=f"Apellido Materno: {aspirante['apellidoMaterno']}"))
            contenido.add_widget(Label(text=f"Estado de Salud: {aspirante['estadoSalud']}"))
            contenido.add_widget(Label(text=f"Genero: {aspirante['genero']}"))
            contenido.add_widget(Label(text=f"Edad: {aspirante['edad']}"))
            contenido.add_widget(Label(text=f"Capacidad Diferente: {aspirante['capacidadDiferente']}"))

            # No es recomendable mostrar la contraseña
            # contenido.add_widget(Label(text=f"Password: {aspirante['password']}"))

            btn_cerrar = Button(text='Cerrar', size_hint_y=None, height=40)
            contenido.add_widget(btn_cerrar)

            popup = Popup(title='Información del Aspirante', content=contenido, size_hint=(0.8, 0.6))
            btn_cerrar.bind(on_release=popup.dismiss)
            popup.open()
        else:
            popup = Popup(title='Error',
                          content=Label(text='No se encontró información del Líder para la educación comunitaria.'),
                          size_hint=(0.6, 0.4))
            popup.open()

    def mostrar_popup_observaciones(self, apoyo, nuevo_estado):
        # Popup para escribir observaciones y número de cuenta
        contenido = BoxLayout(orientation='vertical', spacing=10, padding=10)

        contenido.add_widget(Label(text=f"Cambiar estado a '{nuevo_estado}' para el apoyo ID {apoyo['id_apoyo']}."))
        contenido.add_widget(Label(text="Escribe tus observaciones:"))

        observaciones_input = TextInput(hint_text="Escribe aquí...", multiline=True, size_hint_y=None, height=100)
        contenido.add_widget(observaciones_input)

        contenido.add_widget(Label(text="Fecha de pago (YYYY-MM-DD):"))
        fecha_pago_input = TextInput(hint_text="YYYY-MM-DD", size_hint_y=None, height=40)  # Cambiar número de cuenta por fecha
        contenido.add_widget(fecha_pago_input)


        btn_confirmar = Button(text='Confirmar', size_hint_y=None, height=40)
        btn_cancelar = Button(text='Cancelar', size_hint_y=None, height=40)

        botones = BoxLayout(size_hint_y=None, height=50, spacing=10)
        botones.add_widget(btn_confirmar)
        botones.add_widget(btn_cancelar)

        contenido.add_widget(botones)

        popup = Popup(title="Cambiar Estado", content=contenido, size_hint=(0.8, 0.6))

        btn_confirmar.bind(on_release=lambda btn: self.cambiar_estado(apoyo, nuevo_estado, observaciones_input.text, fecha_pago_input.text, popup))
        btn_cancelar.bind(on_release=popup.dismiss)

        popup.open()

    
    def cambiar_estado(self, apoyo, nuevo_estado, observaciones, fecha_pago, popup):
        # Validar campos
        
        if not observaciones.strip():
            error_popup = Popup(
                title="Error",
                content=Label(text="Las observaciones no pueden estar vacías."),
                size_hint=(0.6, 0.4)
            )
            error_popup.open()
            return

        def fecha_valida(fecha):
            # Validar el formato de fecha como YYYY-MM-DD
            patron = r"^\d{4}-\d{2}-\d{2}$"
            return re.match(patron, fecha) is not None
        
        if not fecha_valida(fecha_pago):
            error_popup = Popup(
                title="Error",
                content=Label(text="Fecha inválida. Usa el formato YYYY-MM-DD."),
                size_hint=(0.6, 0.4)
            )
            error_popup.open()
            return

        # Actualizar el estado, las observaciones y el número de cuenta en la base de datos
        update_query = """
        UPDATE apoyo_educador
        SET estado_apoyo = %s, observaciones = %s, fecha_pago = %s
        WHERE id_apoyo = %s AND id_educador = %s
        """
        execute_non_query(update_query, (nuevo_estado, observaciones, fecha_pago, apoyo['id_apoyo'], apoyo['id_educador']))
        self.conexion.commit()

        popup.dismiss()

        # Mostrar mensaje de confirmación
        success_popup = Popup(
            title="Estado Actualizado",
            content=Label(text=f"El estado ha sido cambiado a '{nuevo_estado}' para el apoyo ID {apoyo['id_apoyo']}"),
            size_hint=(0.6, 0.4)
        )
        success_popup.open()

        # Refrescar la lista de apoyos
        self.crear_grid_apoyos()

    def go_back(self, instance):
        App.get_running_app().root.current = 'departamento_becas'

if __name__ == '__main__':
    ApoyosSolicitadosWindow().run()