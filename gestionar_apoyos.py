import json
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
import pyodbc
from db_connection import execute_query, execute_non_query

# Datos de conexión
server = 'conafe-server.database.windows.net'
database = 'conafe-database'
username = 'admin-conafe'
password = 'MateriaAcaba08/01/25'
driver = '{ODBC Driver 17 for SQL Server}'

class ApoyosSolicitadosWindow(BoxLayout):
    def __init__(self, id_Usuario = None,**kwargs):
        super().__init__(**kwargs)

        self.id_Usuario = id_Usuario

        with self.canvas.before:
            # Define el color (R, G, B, A)
            Color(0.5, 0.5, 0.5, 1)  # Azul
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # Actualiza el rectángulo cuando el tamaño o posición cambian
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.conexion = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        self.cursor = self.conexion.cursor()

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


    def crear_grid_apoyos(self):
        # Limpiar el contenido anterior del scroll_view
        self.scroll_view.clear_widgets()

        grid = GridLayout(cols=5, size_hint_y=None, row_default_height=40, spacing=5)
        grid.bind(minimum_height=grid.setter('height'))

        # Encabezados de tabla
        # grid.add_widget(Label(text='ID Apoyo', bold=True))
        grid.add_widget(Label(text='Fehca de Solicitud', bold=True))
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
            ae.estado_apoyo,
            ae.fecha_solicitud
        FROM apoyo_educador ae
        JOIN apoyo_economico aeco ON ae.id_apoyo = aeco.id_apoyo
        JOIN Usuario u ON ae.id_educador = u.id_Usuario
        """
        apoyos = execute_query(query)

        # Lista de estados posibles
        estados = ['Aceptado', 'Rechazado', 'Congelado']

        for apoyo in apoyos:
            print(apoyo)
            grid.add_widget(Label(text=str(apoyo[6])))
            grid.add_widget(Label(text=apoyo[2]))

            # Botón "Ver" para mostrar información del aspirante
            btn_ver_aspirante = Button(text='Ver', size_hint_y=None, height=40)
            # Capturar el apoyo actual en el lambda para evitar problemas de alcance
            btn_ver_aspirante.bind(on_release=lambda btn, a=apoyo: self.ver_informacion_aspirante(a))
            grid.add_widget(btn_ver_aspirante)

            grid.add_widget(Label(text=apoyo[5]))

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
        id_educador = apoyo[4]
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
        WHERE u.id_Usuario = ?
        """
        aspirante = execute_query(query,(id_educador,))
        aspirante = aspirante[0]

        print("Aspirante:", aspirante)
        if aspirante:
            contenido = BoxLayout(orientation='vertical', spacing=10, padding=10)
            contenido.add_widget(Label(text=f"Correo: {aspirante[1]}"))
            contenido.add_widget(Label(text=f"Rol: {aspirante[2]}"))
            contenido.add_widget(Label(text=f"Nombre: {aspirante[3]}"))
            contenido.add_widget(Label(text=f"Apellido Paterno: {aspirante[4]}"))
            contenido.add_widget(Label(text=f"Apellido Materno: {aspirante[5]}"))
            contenido.add_widget(Label(text=f"Estado de Salud: {aspirante[6]}"))
            contenido.add_widget(Label(text=f"Genero: {aspirante[7]}"))
            contenido.add_widget(Label(text=f"Edad: {aspirante[8]}"))
            contenido.add_widget(Label(text=f"Capacidad Diferente: {aspirante[9]}"))

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
        print(f'apoyo:{apoyo}')
        print(f'nuevo estado: {nuevo_estado}')
        # Popup para escribir observaciones y número de cuenta
        contenido = BoxLayout(orientation='vertical', spacing=10, padding=10)

        contenido.add_widget(Label(text=f"Cambiar estado a '{nuevo_estado}' para el apoyo ID {apoyo[0]}."))
        contenido.add_widget(Label(text="Escribe tus observaciones:"))

        observaciones_input = TextInput(hint_text="Escribe aquí...", multiline=True, size_hint_y=None, height=100)
        contenido.add_widget(observaciones_input)

        btn_confirmar = Button(text='Confirmar', size_hint_y=None, height=40)
        btn_cancelar = Button(text='Cancelar', size_hint_y=None, height=40)

        botones = BoxLayout(size_hint_y=None, height=50, spacing=10)
        botones.add_widget(btn_confirmar)
        botones.add_widget(btn_cancelar)

        contenido.add_widget(botones)

        popup = Popup(title="Cambiar Estado", content=contenido, size_hint=(0.8, 0.6))

        btn_confirmar.bind(on_release=lambda btn: self.cambiar_estado(apoyo, nuevo_estado, observaciones_input.text, popup))
        btn_cancelar.bind(on_release=popup.dismiss)

        popup.open()

    
    def cambiar_estado(self, apoyo, nuevo_estado, observaciones, popup):
        # Validar campos
        
        if not observaciones.strip():
            error_popup = Popup(
                title="Error",
                content=Label(text="Las observaciones no pueden estar vacías."),
                size_hint=(0.6, 0.4)
            )
            error_popup.open()
            return

        # Obtener el estado anterior del apoyo
        estado_anterior = apoyo[5]

        # Actualizar el estado, las observaciones y el número de cuenta en la base de datos
        update_query = """
        UPDATE apoyo_educador
        SET estado_apoyo = ?, observaciones = ?
        WHERE id_apoyo = ? AND id_educador = ?
        """
        self.cursor.execute(update_query, (nuevo_estado, observaciones, apoyo[0], apoyo[4]))
        self.conexion.commit()

        # Insertar el cambio en la tabla cambios_estado_solicitud
        insert_cambio_query = """
        INSERT INTO cambios_estado_solicitud (id_apoyo, id_educador, estado_anterior, estado_actual, fecha_cambio, usuario_responsable, comentario)
        VALUES (?, ?, ?, ?, GETDATE(), ?, ?)
        """
        usuario_responsable = self.id_Usuario
        self.cursor.execute(insert_cambio_query, (
            apoyo[0],        # ID del apoyo
            apoyo[4],    # ID del educador
            estado_anterior,         # Estado anterior
            nuevo_estado,            # Nuevo estado
            usuario_responsable,     # Usuario que realizó el cambio
            observaciones            # Comentarios
        ))
        self.conexion.commit()

        # Modificar el estado de los tickets si el apoyo fue congelado
        if nuevo_estado == 'Congelado':
            if estado_anterior == 'Aceptado':
                self.actualizar_tickets_estado(apoyo[0], apoyo[4], 'Pendiente')

        # Generar los tickets si el apoyo es aprobado
        if nuevo_estado == 'Aceptado':
            if estado_anterior != 'Aceptado':
                self.generar_tickets(apoyo[4], apoyo[0])
            else:
                self.actualizar_tickets_estado(apoyo[0], apoyo[4], 'Pendiente')


        popup.dismiss()

        # Mostrar mensaje de confirmación
        success_popup = Popup(
            title="Estado Actualizado",
            content=Label(text=f"El estado ha sido cambiado a '{nuevo_estado}' para el apoyo ID {apoyo[0]}"),
            size_hint=(0.6, 0.4)
        )
        success_popup.open()

        # Refrescar la lista de apoyos
        self.crear_grid_apoyos()


    def actualizar_tickets_estado(self, id_apoyo, id_educador, nuevo_estado):
        # Cambiar el estado de los tickets dependiendo del estado del apoyo
        estado_ticket = 'Cancelado' if nuevo_estado == 'Cancelado' else 'Pendiente'

        update_query = """
        UPDATE tickets_pago
        SET estado = ?
        WHERE id_apoyo = ? AND id_educador = ? AND estado = 'Pendiente'
        """
        self.cursor.execute(update_query, (estado_ticket, id_apoyo, id_educador))
        self.conexion.commit()

        print(f"Tickets actualizados a estado: {estado_ticket}.")

    def generar_tickets(self, id_educador, id_apoyo):
        # Consultar información del apoyo
        query = """
        SELECT 
            aeco.monto_apoyo,
            aeco.meses_entrega,
            ae.estado_apoyo
        FROM apoyo_educador ae
        JOIN apoyo_economico aeco ON ae.id_apoyo = aeco.id_apoyo
        WHERE ae.id_educador = ? AND ae.id_apoyo = ?
        """
        self.cursor.execute(query, (id_educador, id_apoyo))
        apoyo = self.fetch_as_dict(self.cursor, fetch_one=True)

        if not apoyo or apoyo['estado_apoyo'] != 'Aceptado':
            print("No se pueden generar tickets: el apoyo no está aceptado.")
            return

        # Generar un ticket por cada mes del periodo de entrega
        meses_entrega = json.loads(apoyo['meses_entrega'])  # Lista de meses como "Enero", "Febrero", etc.
        monto_apoyo = apoyo['monto_apoyo']

        for mes in meses_entrega:
            # Insertar el ticket en la base de datos
            insert_ticket_query = """
            INSERT INTO tickets_pago (id_educador, id_apoyo, mes, monto)
            VALUES (?, ?, ?, ?)
            """
            self.cursor.execute(insert_ticket_query, (id_educador, id_apoyo, mes, monto_apoyo))

        self.conexion.commit()
        print("Tickets generados exitosamente.")

    def on_stop(self):
        self.cursor.close()
        self.conexion.close()

    def go_back(self, instance):
        App.get_running_app().root.current = 'departamento_becas'

if __name__ == '__main__':
    ApoyosSolicitadosWindow().run()