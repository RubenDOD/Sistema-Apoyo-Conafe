import re
import mysql.connector
import pyodbc
from kivy.properties import StringProperty
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.spinner import Spinner
from functools import partial
from kivy.uix.button import Button
from kivy.uix.label import Label
from gestionar_apoyos import ApoyosSolicitadosWindow
from interfaz_becas import BecasWindow
from solicitar_apoyo import SolicitarApoyoWindow
from convocatorias import ConvocatoriaWindow  # Importar ConvocatoriaWindow
from aplicarAspirante import aplicarAspiranteWindow  # Importa la ventana aplicarAspirante
from FII import MainWidget  # Importa el widget principal de la pantalla FII
from asignacion import AdminWindowAsignaciones  # Importa AdminWindowAsignaciones desde asignación.py
from capacitador_aspirante import CapacitadorAspiranteWindow  # Importa la ventana capacitadorAspirante
from aspirante_seguimiento import AspiranteSeguimientoWindow  # Importa la ventana aspirante_seguimiento
from CCTs import CCTsWindow
from alumnos import AlumnosWindow
from AsignarAlumno import AsignarAlumnosWindow
from Calificaciones import AlumnosCalificaciones
from Regularizaciones import Regularizaciones
from estimaciontallas import EstimacionTallasScreen
from EE import EquipamientoScreen
from UpdateCorreo import UpdateCorreoWindow
from db_connection import execute_query

# Cargar todos los archivos .kv
Builder.load_file('main.kv')
Builder.load_file('convocatorias.kv')  # Asegúrate de que el archivo convocatorias.kv esté disponible
#Builder.load_file('admin.kv')          # Asegúrate de que el archivo admin.kv esté disponible
Builder.load_file('aplicarAspirante.kv')  # Asegura la carga de aplicarAspirante.kv aquí
Builder.load_file('FII.kv')
Builder.load_file('asignacion.kv')
Builder.load_file('capacitador_aspirante.kv')
Builder.load_file('CCTs.kv')
Builder.load_file("alumnos.kv")
Builder.load_file("AsignarAlumno.kv")
Builder.load_file("interfaz_becas.kv")
Builder.load_file("progreso_apoyos.kv")
Builder.load_file("estimaciontallas.kv")
Builder.load_file("UpdateCorreo.kv")
Builder.load_file("EE.kv")

class CustomBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(CustomBoxLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.06, 0.52, 0.52, 1)  # Fondo color teal oscuro
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class LoginScreen(CustomBoxLayout):
    def verificar_credenciales(self):
        usuario = self.ids.txt_usuario.text
        contrasena = self.ids.txt_contrasena.text
        consulta = f"SELECT acceso, id_Usuario FROM Usuario WHERE correo='{usuario}' AND password='{contrasena}'"
        resultado = execute_query(consulta)

        print(resultado)
        
        if resultado:
            acceso, id_usuario = resultado[0]
            id_usuario = str(id_usuario)
            self.ids.lbl_estado.text = "Login exitoso!"
            
            app = App.get_running_app()
            sm = app.root  # Accede al ScreenManager principal
            
            # Imprimir el ID del usuario para verificación
            print(f"ID de usuario en verificar_credenciales: {id_usuario}")

            # Seleccionar pantalla según el rol
            if acceso == 'Aspirante':
                sm.current = 'aspirante'
                aspirante_screen = sm.get_screen('aspirante').children[0]
                aspirante_screen.id_usuario = id_usuario
                print(f"ID de usuario asignado en AspiranteScreen desde verificar_credenciales: {aspirante_screen.id_usuario}")
                sm.current = 'aspirante'
            elif acceso == 'Miembro Dirección Territorial':
                sm.current = 'vista_direccion_territorial'
            elif acceso == 'LEC':
                lec_screen = sm.get_screen('lec').children[0]
                lec_screen.id_usuario = id_usuario
                lec_screen.cargar_informacion()
                sm.current = 'lec'
            elif acceso == 'Capacitador':
                sm.current = 'capacitador'
                capacitador_screen = sm.get_screen('capacitador').children[0]
                capacitador_screen.id_usuario = id_usuario
                print(f"ID de usuario asignado en CapacitadorScreen desde verificar_credenciales: {capacitador_screen.id_usuario}")
                sm.current = 'capacitador'
            elif acceso == 'Control Escolar':
                # Obtener el CCT asociado
                consulta_cct = f"SELECT CCT FROM AreaControlEscolar WHERE id_ACT = '{id_usuario}'"
                resultado_cct = execute_query(consulta_cct)
                
                if resultado_cct:
                    cct = resultado_cct[0]  # Extraer el valor del CCT
                else:
                    cct = "N/A"  # Si no hay un CCT asignado

                # Pasar el valor de CCT a la pantalla
                control_escolar_screen = sm.get_screen('vista_control_escolar').children[0]
                control_escolar_screen.cct = cct
                
                sm.current = 'vista_control_escolar'
            elif acceso == 'Departamento Becas':
                print("Creando pantalla de departamento de becas...")
                sm.current = 'departamento_becas'
            elif acceso == 'Departamento Equipamiento':
                print("Creando pantalla de departamento de tallas y equipamiento...")
                sm.current = 'departamento_equipamiento'
        else:
            self.ids.lbl_estado.text = "Usuario o contraseña incorrectos."

    def go_to_register(self):
        App.get_running_app().root.current = 'register'
    
    def limpiar_campos(self):
        """Limpia los campos de texto cuando se regresa al login."""
        self.ids.txt_usuario.text = ""
        self.ids.txt_contrasena.text = ""
        self.ids.lbl_estado.text = ""

class RegisterScreen(CustomBoxLayout):
    def registrar_usuario(self):
        usuario = self.ids.txt_usuario.text
        contrasena = self.ids.txt_contrasena.text
        rol = self.ids.spinner_rol.text
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", usuario):
            self.ids.lbl_estado.text = "Por favor ingresa un correo electrónico válido."
            return
        
        if len(contrasena) < 8:
            self.ids.lbl_estado.text = "La contraseña debe tener al menos 8 caracteres."
            return
        
        if rol == 'Seleccionar rol':
            self.ids.lbl_estado.text = "Por favor selecciona un rol."
            return

        if rol == 'Miembro Dirección Territorial' and not usuario.endswith("@conafe.gob.mx"):
            self.ids.lbl_estado.text = "El correo debe tener la terminación @conafe.gob.mx para este rol."
            return

        consulta_verificacion = f"SELECT * FROM Usuario WHERE correo='{usuario}'"
        resultado = execute_query(consulta_verificacion)
        
        if resultado:
            self.ids.lbl_estado.text = "El usuario ya está registrado."
            return

        consulta_registro = f"INSERT INTO Usuario (correo, password, acceso) VALUES ('{usuario}, '{contrasena}', '{rol}')"
        execute_query(consulta_registro)
        
        self.ids.lbl_estado.text = "Registro exitoso. Ahora puedes iniciar sesión."
        App.get_running_app().root.current = 'login'

    def go_back(self):
        App.get_running_app().root.current = 'login'

class AspiranteScreen(CustomBoxLayout):
    id_usuario = StringProperty()

    def __init__(self, **kwargs):
        super(AspiranteScreen, self).__init__(**kwargs)

    def aplicar_a_convocatoria(self):
        app = App.get_running_app()
        app.root.current = 'aplicar_aspirante'  # Redirige a la pantalla de aplicación

    def interfazAspiranteSeguimiento(self, instance):
        print(f"ID de usuario en AspiranteScreen: {self.id_usuario}")
        # Crea una instancia de CapacitadorAspiranteWindow pasando el id_usuario actual
        app = App.get_running_app()
        aspirante_seguimiento_window = AspiranteSeguimientoWindow(id_usuario=self.id_usuario)
        aspirante_seguimiento_screen = app.root.get_screen('aspirante_seguimiento')
        aspirante_seguimiento_screen.clear_widgets()
        aspirante_seguimiento_screen.add_widget(aspirante_seguimiento_window)

        # Cambia a la pantalla de capacitador_aspirante
        app.root.current = 'aspirante_seguimiento'

class AspiranteSeguimientoScreen(CustomBoxLayout):
    id_usuario = StringProperty()
    def __init__(self, **kwargs):
        super(AspiranteSeguimientoScreen, self).__init__(**kwargs)
        # Crear una instancia de AspiranteSeguimientoWindow y pasar id_usuario
        self.add_widget(AspiranteSeguimientoWindow(self.id_usuario))

class VistaDireccionTerritorialScreen(CustomBoxLayout):
    def __init__(self, **kwargs):
        super(VistaDireccionTerritorialScreen, self).__init__(**kwargs)
        # Configuración de los botones

    def interfaz_convocatorias(self, instance):
        # Cambia a la pantalla de Convocatorias
        app = App.get_running_app()
        app.root.current = 'convocatorias'
    
    def interfaz_capacitaciones(self, instance):
        # Cambia a la pantalla de capacitaciones
        app = App.get_running_app()
        app.root.current = 'capacitaciones'  # Cambia a la pantalla de capacitaciones
    
    def interfaz_cct_practicas(self, instance):
        # Cambia a la pantalla de CCT Capacitaciones
        app = App.get_running_app()
        app.root.current = 'asignacion_cct_practicas'
    
    def interfaz_tablero_control(self, instance):
        # Cambia a la pantalla de tablero de control
        app = App.get_running_app()
        app.root.current = 'tablero de control'

class ConvocatoriasScreen(Screen):  # Modificar para heredar de Screen
    def __init__(self, **kwargs):
        super(ConvocatoriasScreen, self).__init__(**kwargs)
        self.add_widget(ConvocatoriaWindow())  # Agregar ConvocatoriaWindow como widget principal

class CapacitacionesScreen(Screen):
    def __init__(self, **kwargs):
        super(CapacitacionesScreen, self).__init__(**kwargs)
        self.admin_window = AdminWindowAsignaciones()  # Instancia única de AdminWindowAsignaciones

    def on_enter(self):
        # Limpiar todos los widgets de la pantalla antes de añadir el contenido
        self.clear_widgets()  # Asegúrate de que la pantalla esté vacía
        self.add_widget(self.admin_window)  # Añade la instancia única de AdminWindowAsignaciones

class AsignarCCTPracticasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Inicializando AsignacionCCTPracticasScreen...")

    def on_kv_post(self, base_widget):
        print("Cargando datos en AsignacionCCTPracticasScreen...")
        self.load_data()

    def load_data(self):
        try:
            print("Conectando a la base de datos...")
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            cursor = db.cursor()

            # Consulta SQL
            query = """
                SELECT 
                    A.id_Aspirante, 
                    CONCAT(A.nombres, ' ', A.apellidoPaterno, ' ', A.apellidoMaterno) AS nombre_completo
                FROM Aspirante A
                JOIN Usuario U
                    ON A.id_Aspirante = U.id_Usuario -- Relación entre Aspirante y Usuario
                LEFT JOIN AsignacionAspiranteCCT ACCT 
                    ON A.id_Aspirante = ACCT.id_Aspirante -- Verifica si el aspirante está asignado a un CCT
                JOIN FII 
                    ON A.id_Aspirante = FII.id_Aspirante -- Relación con el estado de la capacitación
                WHERE 
                    FII.estadoCapacitacion = 'Finalizado' -- Verifica que el estado de la capacitación sea 'Finalizado'
                    AND ACCT.id_Aspirante IS NULL -- Asegura que el aspirante no esté asignado a ningún CCT
                    AND U.acceso = 'Aspirante'; -- Asegura que el usuario sea un aspirante
            """
            cursor.execute(query)
            aspirantes = cursor.fetchall()
            db.close()

            print("Datos recuperados:", aspirantes)

            # Limpiar widgets existentes
            self.ids.data_layout.clear_widgets()

            for aspirante in aspirantes:
                name_btn = Button(
                    text=aspirante[1],
                    size_hint_y=None,
                    height=50,
                    background_color=(0.0, 0.4, 0.4, 1),
                    color=(1, 1, 1, 1)
                )
                self.ids.data_layout.add_widget(name_btn)

                action_btn = Button(
                    text="Asignar CCT",
                    size_hint_y=None,
                    height=50,
                    background_color=(0.7, 0, 0, 1),
                    color=(1, 1, 1, 1)
                )
                action_btn.bind(on_release=partial(self.go_to_detalle, aspirante[0]))
                self.ids.data_layout.add_widget(action_btn)

            self.ids.data_layout.height = self.ids.data_layout.minimum_height
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")

    def go_to_detalle(self, aspirante_id, *args):
        # Obtén la pantalla DetalleCCTScreen
        detalle_screen = self.manager.get_screen("mostrar ccts")

        # Limpiar widgets antes de cargar nuevos datos
        detalle_screen.ids.cct_list.clear_widgets()

        # Establece el aspirante_id en la pantalla de detalle
        detalle_screen.load_initial_ccts(aspirante_id)

        # Cambia a la pantalla de detalle
        self.manager.current = "mostrar ccts"

    def go_back(self):
        if self.manager:
            self.manager.current = 'vista_direccion_territorial'

class DetalleCCTScreen(Screen):
    def load_initial_ccts(self, aspirante_id):
        self.aspirante_id = aspirante_id
        print(f"Cargando CCT iniciales para aspirante con ID: {aspirante_id}...")  # Debug
        try:
            # Limpiar widgets previos
            self.ids.cct_list.clear_widgets()

            # Conexión a la base de datos
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            cursor = db.cursor()

            # Consulta de datos del aspirante
            query_aspirante = """
                SELECT 
                    ParticipacionAspirante.estado AS estado_interes, 
                    ParticipacionAspirante.municipio AS municipio_interes, 
                    InfoEducativaAspirante.nivelEducativo,
                    CONCAT(Aspirante.nombres, ' ', Aspirante.apellidoPaterno, ' ', Aspirante.apellidoMaterno) AS nombre_completo
                FROM ParticipacionAspirante
                JOIN InfoEducativaAspirante 
                    ON ParticipacionAspirante.id_Aspirante = InfoEducativaAspirante.id_Aspirante
                JOIN Aspirante 
                    ON ParticipacionAspirante.id_Aspirante = Aspirante.id_Aspirante
                WHERE ParticipacionAspirante.id_Aspirante = %s;
            """
            cursor.execute(query_aspirante, (aspirante_id,))
            aspirante_data = cursor.fetchone()

            if not aspirante_data:
                print("No se encontraron datos del aspirante.")  # Debug
                return

            estado, municipio, nivel_educativo, nombre_completo = aspirante_data
            estado = estado.replace("CONAFE ", "").strip()

            # Si el municipio es "NO SE", o no se encuentra en los CCT, se define como texto vacío
            if municipio.upper() == "NO SE":
                municipio = ""

            print(f"Ubicación: {estado}, {municipio}, Nivel Educativo: {nivel_educativo}, Nombre: {nombre_completo}")  # Debug

            self.ids.aspirante_info.text = (
                f"Datos del Aspirante:\n"
                f"Nombre: {nombre_completo}\n"
                f"Estado preferible: {estado}\n"
                f"Municipio preferible: {municipio}\n"
                f"Nivel Educativo: {nivel_educativo}"
            )
            self.estado_aspirante = estado
            self.municipio_aspirante = municipio
            self.nivel_educativo = nivel_educativo

            # Buscar CCT iniciales
            query_ccts = """
            SELECT claveCentro, nombre, estado, municipio, nivelEducativo, cupos_disponibles
            FROM CCT
            WHERE estado = %s AND nivelEducativo = %s AND cupos_disponibles > 0
            ORDER BY estado, municipio;
            """
            cursor.execute(query_ccts, (estado, nivel_educativo))
            ccts = cursor.fetchall()
            db.close()

            print("CCT iniciales recuperados:", ccts)  # Debug

            # Mostrar resultados iniciales
            for cct in ccts:
                row = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=50,
                    spacing=10
                )

                # Añadir etiquetas para los datos del CCT
                row.add_widget(Label(
                    text=f"{cct[0]}",  # Número de CCT
                    size_hint_x=0.15,  # Ajustar ancho relativo
                    halign='center',
                    valign='middle',
                    color=(1, 1, 1, 1)
                ))
                row.add_widget(Label(
                    text=f"{cct[1]}",  # Nombre del CCT
                    size_hint_x=0.25,
                    halign='center',
                    valign='middle',
                    color=(1, 1, 1, 1)
                ))
                row.add_widget(Label(
                    text=f"{cct[2]}",  # Estado
                    size_hint_x=0.15,
                    halign='center',
                    valign='middle',
                    color=(1, 1, 1, 1)
                ))
                row.add_widget(Label(
                    text=f"{cct[3]}",  # Municipio
                    size_hint_x=0.15,
                    halign='center',
                    valign='middle',
                    color=(1, 1, 1, 1)
                ))
                row.add_widget(Label(
                    text=f"{cct[4]}",  # Grado Educativo
                    size_hint_x=0.15,
                    halign='center',
                    valign='middle',
                    color=(1, 1, 1, 1)
                ))
                row.add_widget(Label(
                    text=f"{cct[5]}",  # Cupos Disponibles
                    size_hint_x=0.1,
                    halign='center',
                    valign='middle',
                    color=(1, 1, 1, 1)
                ))

                # Añadir botón para asignar
                action_btn = Button(
                    text="Asignar",
                    size_hint_x=0.1,
                    background_color=(0.7, 0, 0, 1),
                    color=(1, 1, 1, 1)
                )
                action_btn.bind(on_release=partial(self.assign_cct_confirm, self.aspirante_id, cct[0]))
                row.add_widget(action_btn)

                self.ids.cct_list.add_widget(row)
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")

    def search_ccts(self, *args):
        estado = self.ids.search_estado.text.strip()
        municipio = self.ids.search_municipio.text.strip()

        print(f"Buscando CCTs por Estado: {estado}, Municipio: {municipio}...")  # Debug
        try:
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            cursor = db.cursor()

            # Construir consulta dinámica según los campos de búsqueda
            query = """
            SELECT claveCentro, nombre, estado, municipio, nivelEducativo, cupos_disponibles
            FROM CCT
            WHERE nivelEducativo = %s
            """
            params = [self.nivel_educativo]

            if estado:
                query += " AND estado = %s"
                params.append(estado)
            if municipio:
                query += " AND municipio = %s"
                params.append(municipio)

            query += " ORDER BY estado, municipio;"
            cursor.execute(query, tuple(params))
            ccts = cursor.fetchall()
            db.close()

            print("CCTs recuperados:", ccts)  # Debug

            # Mostrar resultados
            self.ids.cct_list.clear_widgets()
            for cct in ccts:
                cct_info = (
                    f"[b]Número de CCT:[/b] {cct[0]}\n"
                    f"[b]Nombre:[/b] {cct[1]}\n"
                    f"[b]Estado:[/b] {cct[2]}\n"
                    f"[b]Municipio:[/b] {cct[3]}\n"
                    f"[b]Grado Educativo:[/b] {cct[4]}\n"
                    f"[b]Cupos Disponibles:[/b] {cct[5]}"
                )
                cct_btn = Button(
                    text=cct_info,
                    size_hint_y=None,
                    height=150,
                    markup=True,
                    background_color=(0.0, 0.4, 0.4, 1),
                    color=(1, 1, 1, 1)
                )
                cct_btn.bind(on_release=partial(self.assign_cct_confirm, self.aspirante_id, cct[0]))
                self.ids.cct_list.add_widget(cct_btn)

        except mysql.connector.Error as err:
            print(f"Error al buscar CCTs: {err}")

    def assign_cct_confirm(self, aspirante_id, clave_centro, *args):
        # Mostrar un botón de confirmación
        self.ids.cct_list.clear_widgets()
        confirmation_label = Label(
            text=f"¿Estás seguro de asignar el CCT {clave_centro} al aspirante?",
            size_hint_y=None,
            height=50,
            color=(1, 1, 1, 1)
        )
        confirm_button = Button(
            text="Confirmar Asignación",
            size_hint_y=None,
            height=50,
            background_color=(0.0, 0.6, 0.0, 1),
            color=(1, 1, 1, 1)
        )
        confirm_button.bind(on_release=partial(self.assign_cct, aspirante_id, clave_centro))

        cancel_button = Button(
            text="Cancelar",
            size_hint_y=None,
            height=50,
            background_color=(0.6, 0.0, 0.0, 1),
            color=(1, 1, 1, 1)
        )
        cancel_button.bind(on_release=self.reload_ccts)

        self.ids.cct_list.add_widget(confirmation_label)
        self.ids.cct_list.add_widget(confirm_button)
        self.ids.cct_list.add_widget(cancel_button)

    def assign_cct(self, aspirante_id, clave_centro, *args):
        print(f"Asignando CCT {clave_centro} al aspirante {aspirante_id}...")  # Debug
        try:
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            cursor = db.cursor()

            # Insertar asignación en la tabla
            query_assign = """
            INSERT INTO AsignacionAspiranteCCT (id_Aspirante, claveCentro, fecha_asignacion)
            VALUES (%s, %s, CURDATE());
            """
            cursor.execute(query_assign, (aspirante_id, clave_centro))

            # Actualizar cupos disponibles en el CCT
            query_update_cupos = """
            UPDATE CCT SET cupos_disponibles = cupos_disponibles - 1 WHERE claveCentro = %s;
            """
            cursor.execute(query_update_cupos, (clave_centro,))

            # Actualizar cupos disponibles en el CCT
            query_update_LEC = """
            UPDATE USUARIO SET acceso = 'LEC' WHERE id_Usuario = %s;
            """
            cursor.execute(query_update_LEC, (aspirante_id,))
            db.commit()
            db.close()

            print("CCT asignado correctamente.")  # Debug

            # Redirigir al usuario al AsignacionCCTPracticasScreen y recargar los datos
            self.manager.current = "asignacion_cct_practicas"
            self.manager.get_screen("asignacion_cct_practicas").load_data()
        except mysql.connector.Error as err:
            print(f"Error al asignar CCT: {err}")

    def reload_ccts(self, *args):
        # Recarga la lista inicial de CCTs
        self.load_initial_ccts(self.aspirante_id)

    def go_back(self):
        if self.manager:
            print("Regresando a AsignacionCCTPracticasScreen...")
            self.manager.current = 'asignacion_cct_practicas'
            self.manager.get_screen('asignacion_cct_practicas').load_data()
        else:
            print("Error: ScreenManager no está configurado.")

# Define la pantalla Tablero de Control
class TableroControlScreen(Screen):
    def __init__(self, **kwargs):
        super(TableroControlScreen, self).__init__(**kwargs)
    
    def regresar_vista_direccion(self):
        app = App.get_running_app()
        app.root.current = 'vista_direccion_territorial'

    def go_to_fii_screen(self):
        app = App.get_running_app()
        app.root.current = 'fii'

class LECScreen(CustomBoxLayout):
    id_usuario = StringProperty("")  # Almacena el ID del LEC
    cct = StringProperty("No asignado")  # Almacena el CCT del LEC
    grupo = StringProperty("Sin grupo asignado")  # Almacena el grupo del LEC

    def cargar_informacion(self):
        """
        Carga la información del CCT y del grupo asignado al LEC.
        """

        try:
            # Consulta para obtener el CCT y grupo asignado al LEC
            query = f"""
                SELECT 
                AsignacionAspiranteCCT.claveCentro AS cct,
                CCTgrupos.nombre_grupo AS grupo
                FROM AsignacionAspiranteCCT
                LEFT JOIN CCTgrupos ON AsignacionAspiranteCCT.id_Aspirante = CCTgrupos.id_profesor
                WHERE AsignacionAspiranteCCT.id_Aspirante = '{self.id_usuario}';
            """
            result = execute_query(query)

            # Actualizar las propiedades de la pantalla
            self.cct = result['cct'] if result and result['cct'] else "No asignado"
            self.grupo = result['grupo'] if result and result['grupo'] else "Sin grupo asignado"
        except mysql.connector.Error as err:
            print(f"Error al cargar información del LEC: {err}")
            self.cct = "Error al cargar"
            self.grupo = "Error al cargar"

        # Actualizar los botones dinámicos según la asignación del grupo
        self.actualizar_botones()

    def actualizar_botones(self):
        """
        Actualiza los botones de la pantalla dinámicamente según el grupo asignado.
        """
        self.ids.botones_layout.clear_widgets()  # Limpia los botones existentes

        if self.grupo != "Sin grupo asignado":
            # Agregar los botones solo si el LEC tiene un grupo asignado
            botones = [
                {"text": "Control Escolar", "on_press": self.control_escolar},
                {"text": "Regularizaciones", "on_press": self.control_escolarReg},
            ]
            for boton in botones:
                btn = Button(text=boton['text'], size_hint_y=None, height=50)
                btn.bind(on_press=boton['on_press'])
                self.ids.botones_layout.add_widget(btn)

        # Botón de cerrar sesión (siempre presente)
        btn_cerrar_sesion = Button(
            text="Cerrar Sesión",
            size_hint_y=None,
            height=50,
            on_press=lambda _: self.cerrar_sesion()
        )
        self.ids.botones_layout.add_widget(btn_cerrar_sesion)

        # Botón de update Correo (siempre presente)
        btn_actualizar_contacto = Button(
            text="Actualizar Contacto",
            size_hint_y=None,
            height=50,
            on_press=lambda _: self.update_contacto()
        )
        self.ids.botones_layout.add_widget(btn_actualizar_contacto)

    def opciones_grupo(self):
        print("Opciones del grupo seleccionadas.", self.id_usuario)
        
    def update_contacto(self):
        print("Accediendo a cambiar correo.")
        app = App.get_running_app()

        # Obtener la pantalla de calificaciones
        lec_cambiarCorreo_screen = app.root.get_screen('lec_cambiarCorreo')

        # Obtener el widget AlumnosCalificaciones dentro del Screen
        lec_cambiarCorreo_widget = lec_cambiarCorreo_screen.children[0]

        # Asignar el CCT y grupo a la pantalla de calificaciones
        lec_cambiarCorreo_widget.id_aspirante = self.id_usuario

        # Cambiar a la pantalla de calificaciones
        app.root.current = 'lec_cambiarCorreo'  # Cambia a la pantalla de calificaciones

    def control_escolar(self, instance):
        print("Accediendo a control escolar.")
        app = App.get_running_app()

        # Obtener la pantalla de calificaciones
        lec_calificaciones_screen = app.root.get_screen('lec_calificaciones')

        # Obtener el widget AlumnosCalificaciones dentro del Screen
        lec_calificaciones_widget = lec_calificaciones_screen.children[0]

        # Asignar el CCT y grupo a la pantalla de calificaciones
        lec_calificaciones_widget.cct = self.cct
        lec_calificaciones_widget.grupo = self.grupo

        

        # Llamar al método que carga los alumnos
        lec_calificaciones_widget.load_alumnos()  # Llamamos el método en el widget correcto

        # Cambiar a la pantalla de calificaciones
        app.root.current = 'lec_calificaciones'  # Cambia a la pantalla de calificaciones
    
    def control_escolarReg(self, instance):
        print("Accediendo a control escolar.")
        app = App.get_running_app()


        lec_regularizaciones_screen = app.root.get_screen('lec_regularizaciones')


        lec_regularizaciones_widget = lec_regularizaciones_screen.children[0]

        lec_regularizaciones_widget.cct = self.cct
        lec_regularizaciones_widget.grupo = self.grupo

        lec_regularizaciones_widget.load_alumnos()  # Llamamos el método en el widget correcto

        # Cambiar a la pantalla de calificaciones
        app.root.current = 'lec_regularizaciones'  # Cambia a la pantalla de calificaciones


    def apoyos(self, instance):
        print("Accediendo a apoyos.")
        app = App.get_running_app()

        # Crear una instancia de ApoyosWindow
        apoyos_window = BecasWindow(id_educador = self.id_usuario)
        apoyos_screen = app.root.get_screen('apoyos_economicos')
        apoyos_screen.clear_widgets()
        apoyos_screen.add_widget(apoyos_window)

        # Cambia a la pantalla de apoyos
        app.root.current = 'apoyos_economicos'

    def solicitar_apoyo(self, instance):
        print("Accediendo a solicitar apoyo.")
        app = App.get_running_app()

        # Crear una instancia de SolicitarApoyoWindow
        solicitar_apoyo_window = SolicitarApoyoWindow(id_educador = self.id_usuario)
        solicitar_apoyo_screen = app.root.get_screen('solicitar_apoyo')
        solicitar_apoyo_screen.clear_widgets()
        solicitar_apoyo_screen.add_widget(solicitar_apoyo_window)

        # Cambia a la pantalla de solicitar apoyo
        app.root.current = 'solicitar_apoyo'

    def cerrar_sesion(self):
        """
        Regresa al login y limpia los campos.
        """
        app = App.get_running_app()
        app.root.get_screen('login').children[0].limpiar_campos()
        app.root.current = 'login'


class SolicitarApoyoScreen(CustomBoxLayout):
    def __init__(self, **kwargs):
        super(SolicitarApoyoScreen, self).__init__(**kwargs)

class ApoyosScreen(CustomBoxLayout):
    id_educador = StringProperty()
    def __init__(self, **kwargs):
        super(ApoyosScreen, self).__init__(**kwargs)

class ApoyoProgresoScreen(CustomBoxLayout):
    def __init__(self, **kwargs):
        super(ApoyoProgresoScreen, self).__init__(**kwargs)


class CapacitadorScreen(CustomBoxLayout):
    id_usuario = StringProperty()
    def __init__(self, **kwargs):
        super(CapacitadorScreen, self).__init__(**kwargs)
    
    def interfaz_CapacitadorAspirante(self, instance):
        print(f"ID de usuario en CAPACITADOR: {self.id_usuario}")
        # Crea una instancia de CapacitadorAspiranteWindow pasando el id_usuario actual
        app = App.get_running_app()
        capacitador_aspirante_window = CapacitadorAspiranteWindow(id_usuario=self.id_usuario)
        capacitador_aspirante_screen = app.root.get_screen('capacitador_aspirante')
        capacitador_aspirante_screen.clear_widgets()
        capacitador_aspirante_screen.add_widget(capacitador_aspirante_window)

        # Cambia a la pantalla de capacitador_aspirante
        app.root.current = 'capacitador_aspirante'

class CapacitadorAspiranteScreen(CustomBoxLayout):
    id_usuario = StringProperty()
    def __init__(self, **kwargs):
        super(CapacitadorAspiranteScreen, self).__init__(**kwargs)
        # Crear una instancia de CapacitadorAspiranteWindow y pasar id_usuario
        self.add_widget(CapacitadorAspiranteWindow(self.id_usuario))

class ControlEscolarScreen(CustomBoxLayout):
    cct = StringProperty("")  # Propiedad para almacenar el CCT asociado

class vistaAsignarGrupoLEC(CustomBoxLayout):
    cct = StringProperty("")  # Clave del CCT asociada

    def cargar_profesores(self):
        """
        Carga todos los profesores (LEC) asignados al CCT y los grupos disponibles para cada uno.
        """
        self.ids.grid_profesores.clear_widgets()  # Limpiar la lista de profesores
        profesores = self.obtener_lecs_por_cct()

        if profesores:
            for profesor in profesores:
                box = BoxLayout(size_hint_y=None, height=50, spacing=10)
                box.add_widget(Label(text=profesor['nombre'], size_hint_x=0.5))

                # Spinner para grupos disponibles
                spinner = Spinner(
                    text="Cargando grupos...",
                    size_hint_x=0.3
                )
                spinner.profesor_id = profesor['id']
                spinner.bind(on_press=lambda instance: self.cargar_grupos(instance, profesor['id']))
                box.add_widget(spinner)

                # Botón para confirmar la asignación
                asignar_btn = Button(
                    text="Asignar",
                    size_hint_x=0.2
                )
                asignar_btn.spinner = spinner  # Asociar el spinner con el botón
                asignar_btn.bind(on_press=self.asignar_profesor)
                box.add_widget(asignar_btn)

                self.ids.grid_profesores.add_widget(box)
        else:
            self.ids.grid_profesores.add_widget(Label(text="No hay profesores asignados a este CCT.", size_hint_y=None, height=50))

    def cargar_grupos(self, spinner, profesor_id):
        """
        Carga los grupos disponibles para asignar al profesor seleccionado.
        """
        grupos = self.obtener_grupos_disponibles()

        if grupos:
            spinner.values = [grupo['nombre'] for grupo in grupos]
            spinner.grupo_ids = {grupo['nombre']: grupo['id'] for grupo in grupos}  # Mapeo nombre -> ID
            spinner.text = "Seleccionar grupo"
        else:
            spinner.values = ["No hay grupos disponibles"]
            spinner.grupo_ids = {}  # Sin mapeo
            spinner.text = "No hay grupos disponibles"

    def asignar_profesor(self, instance):
        """
        Asigna el profesor al grupo seleccionado.
        """
        spinner = instance.spinner
        grupo_nombre = spinner.text

        if grupo_nombre == "No hay grupos disponibles" or grupo_nombre == "Cargando grupos...":
            print("No se puede asignar. No hay grupos seleccionados o disponibles.")
            return

        grupo_id = spinner.grupo_ids[grupo_nombre]  # Obtener el ID del grupo
        profesor_id = spinner.profesor_id

        # Ejecutar la asignación
        self.asignar_profesor_a_grupo(profesor_id, grupo_id)

        # Recargar la lista de profesores y grupos
        self.cargar_profesores()

    def obtener_grupos_disponibles(self):
        """
        Devuelve los grupos disponibles (sin profesor asignado) en el CCT.
        """
        try:
            query = """
                SELECT id_grupo AS id, nombre_grupo AS nombre
                FROM CCTgrupos
                WHERE id_CCT = ? AND id_profesor IS NULL;
            """
            grupos = execute_query(query, (self.cct,))
            return [{"id": grupo[0], "nombre": grupo[1]} for grupo in grupos]
        except Exception as err:
            print(f"Error al obtener grupos disponibles: {err}")
            return []


    def asignar_profesor_a_grupo(self, profesor_id, grupo_id):
        """
        Asigna un profesor a un grupo específico.
        """
        try:
            query = """
                UPDATE CCTgrupos
                SET id_profesor = ?
                WHERE id_grupo = ?;
            """
            execute_query(query, (profesor_id, grupo_id))
            print(f"Profesor {profesor_id} asignado al grupo {grupo_id}.")
        except Exception as err:
            print(f"Error al asignar profesor: {err}")


    def obtener_lecs_por_cct(self):
        """
        Consulta todos los LEC asignados al CCT específico.
        """
        try:
            query = """
                SELECT Aspirante.id_Aspirante AS id, 
                    CONCAT(Aspirante.nombres, ' ', Aspirante.apellidoPaterno, ' ', Aspirante.apellidoMaterno) AS nombre
                FROM AsignacionAspiranteCCT
                JOIN Aspirante ON AsignacionAspiranteCCT.id_Aspirante = Aspirante.id_Aspirante
                LEFT JOIN CCTgrupos ON Aspirante.id_Aspirante = CCTgrupos.id_profesor AND CCTgrupos.id_CCT = AsignacionAspiranteCCT.claveCentro
                WHERE AsignacionAspiranteCCT.claveCentro = ? AND CCTgrupos.id_profesor IS NULL;
            """
            lecs = execute_query(query, (self.cct,))
            return [{"id": lec[0], "nombre": lec[1]} for lec in lecs]
        except Exception as err:
            print(f"Error al obtener LECs: {err}")
            return []


class vistaGestionLEC(CustomBoxLayout):
    pass

class vistaGestionAlumnos(CustomBoxLayout):
    pass

class vistaGestionGrupos(CustomBoxLayout):
    pass

class DepartamentoBecasScreen(Screen):
    def gestionar_apoyos(self, instance):
        print("Accediendo a la pantalla de gestión de apoyos")
        app = App.get_running_app()

        # Crear una instancia de la pantalla de gestión de apoyos
        gestion_apoyos_window = ApoyosSolicitadosWindow()
        gestion_apoyos_screen = app.root.get_screen('gestion_apoyos')
        gestion_apoyos_screen.clear_widgets()
        gestion_apoyos_screen.add_widget(gestion_apoyos_window)

        # Mostrar la pantalla de gestión de apoyos
        app.root.current = 'gestion_apoyos'

class ApoyosSolicitadosScreen(CustomBoxLayout):
    def __init__(self, **kwargs):
        super(ApoyosSolicitadosScreen, self).__init__(**kwargs)

class TallasEquipamientoScreen(CustomBoxLayout):
    def __init__(self, **kwargs):
        super(TallasEquipamientoScreen, self).__init__(**kwargs)
    
    def tallas(self):
        print("Accediendo a Tallas")
        app = App.get_running_app()

        # Cambia a la pantalla de tallas
        app.root.current = 'tallas'
    
    def equipamiento(self):
        print("Accediendo a Equipamiento")
        app = App.get_running_app()

        # Cambia a la pantalla de tallas
        app.root.current = 'equipamiento'

class EquipamientoScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        aux = EquipamientoScreen()
        # Cargar la interfaz del equipamiento
        self.add_widget(aux)

class LoginApp(App):
    def build(self):
        sm = ScreenManager()

        screen_login = Screen(name='login')
        screen_login.add_widget(LoginScreen())
        sm.add_widget(screen_login)

        screen_register = Screen(name='register')
        screen_register.add_widget(RegisterScreen())
        sm.add_widget(screen_register)

        screen_aspirante = Screen(name='aspirante')
        screen_aspirante.add_widget(AspiranteScreen())
        sm.add_widget(screen_aspirante)

        screen_aspiranteSeguimiento = Screen(name='aspirante_seguimiento')
        screen_aspiranteSeguimiento.add_widget(AspiranteSeguimientoScreen())    
        sm.add_widget(screen_aspiranteSeguimiento)

        screen_vdt = Screen(name='vista_direccion_territorial')
        screen_vdt.add_widget(VistaDireccionTerritorialScreen())
        sm.add_widget(screen_vdt)

        screen_lec = Screen(name='lec')
        screen_lec.add_widget(LECScreen())
        sm.add_widget(screen_lec)

        screen_lec_calificaciones = Screen(name='lec_calificaciones')
        screen_lec_calificaciones.add_widget(AlumnosCalificaciones())
        sm.add_widget(screen_lec_calificaciones)

        screen_lec_cambiarCorreo = Screen(name='lec_cambiarCorreo')
        screen_lec_cambiarCorreo.add_widget(UpdateCorreoWindow())
        sm.add_widget(screen_lec_cambiarCorreo)

        screen_lec_regularizaciones = Screen(name='lec_regularizaciones')
        screen_lec_regularizaciones.add_widget(Regularizaciones())
        sm.add_widget(screen_lec_regularizaciones)

        screen_ControlEscolar = Screen(name='vista_control_escolar')
        screen_ControlEscolar.add_widget(ControlEscolarScreen())
        sm.add_widget(screen_ControlEscolar)

        screen_vista_gestion_lec = Screen(name='vista_gestion_lec')
        screen_vista_gestion_lec.add_widget(vistaGestionLEC())
        sm.add_widget(screen_vista_gestion_lec)

        screen_vista_asignar_grupo_lec = Screen(name='vista_asignar_grupo_lec')
        screen_vista_asignar_grupo_lec.add_widget(vistaAsignarGrupoLEC())
        sm.add_widget(screen_vista_asignar_grupo_lec)

        screen_vista_gestion_alumnos = Screen(name='vista_gestion_alumnos')
        screen_vista_gestion_alumnos.add_widget(vistaGestionAlumnos())
        sm.add_widget(screen_vista_gestion_alumnos)

        screen_vista_alta_alumnos = Screen(name='vista_alta_alumnos')
        screen_vista_alta_alumnos.add_widget(AlumnosWindow())
        sm.add_widget(screen_vista_alta_alumnos)
    
        screen_vista_asignar_alumnos = Screen(name='vista_asignar_alumnos')
        screen_vista_asignar_alumnos.add_widget(AsignarAlumnosWindow())
        sm.add_widget(screen_vista_asignar_alumnos)

        screen_vista_gestion_grupos = Screen(name='vista_gestion_grupos')
        screen_vista_gestion_grupos.add_widget(vistaGestionGrupos())
        sm.add_widget(screen_vista_gestion_grupos)

        screen_vista_gestion_grupos_detalle = Screen(name='vista_gestion_grupos_detalle')
        screen_vista_gestion_grupos_detalle.add_widget(CCTsWindow())
        sm.add_widget(screen_vista_gestion_grupos_detalle)

        screen_capacitador = Screen(name='capacitador')
        screen_capacitador.add_widget(CapacitadorScreen())
        sm.add_widget(screen_capacitador)

        screen_capacitadorAspirante = Screen(name='capacitador_aspirante')
        screen_capacitadorAspirante.add_widget(CapacitadorAspiranteScreen())
        sm.add_widget(screen_capacitadorAspirante)

        screen_convocatorias = ConvocatoriasScreen(name='convocatorias')  # Usar ConvocatoriasScreen
        sm.add_widget(screen_convocatorias)

        screen_capacitaciones = CapacitacionesScreen(name='capacitaciones')  # Usar CapacitacionScreen
        sm.add_widget(screen_capacitaciones)

        screen_tablero_control = TableroControlScreen(name='tablero de control')  # Usar TableroScreen
        sm.add_widget(screen_tablero_control)

        screen_aplicar_aspirante = Screen(name='aplicar_aspirante')
        screen_aplicar_aspirante.add_widget(aplicarAspiranteWindow())
        sm.add_widget(screen_aplicar_aspirante)

        screen_fii = Screen(name='fii')
        screen_fii.add_widget(MainWidget())
        sm.add_widget(screen_fii)

        screen_asignar_cct_practicas = AsignarCCTPracticasScreen(name='asignacion_cct_practicas') # Usar Asignar CCT Screen
        sm.add_widget(screen_asignar_cct_practicas)

        screen_detalle_cct = DetalleCCTScreen(name='mostrar ccts')
        sm.add_widget(screen_detalle_cct)

        screen_apoyos_economicos = Screen(name='apoyos_economicos')
        screen_apoyos_economicos.add_widget(ApoyosScreen())
        sm.add_widget(screen_apoyos_economicos)

        screen_progreso_apoyo = Screen(name='progreso_apoyo')
        screen_progreso_apoyo.add_widget(ApoyoProgresoScreen())
        sm.add_widget(screen_progreso_apoyo)

        scree_solicitar_apoyo = Screen(name='solicitar_apoyo')
        scree_solicitar_apoyo.add_widget(SolicitarApoyoScreen())
        sm.add_widget(scree_solicitar_apoyo)

        screen_gestion_apoyos = Screen(name='gestion_apoyos')
        screen_gestion_apoyos.add_widget(ApoyosSolicitadosScreen())
        sm.add_widget(screen_gestion_apoyos)

        screen_departamento_becas = Screen(name='departamento_becas')
        screen_departamento_becas.add_widget(DepartamentoBecasScreen())
        sm.add_widget(screen_departamento_becas)

        screen_departamento_equipamiento = Screen(name='departamento_equipamiento')
        screen_departamento_equipamiento.add_widget(TallasEquipamientoScreen())
        sm.add_widget(screen_departamento_equipamiento)

        screen_tallas = Screen(name='tallas')
        screen_tallas.add_widget(EstimacionTallasScreen())
        sm.add_widget(screen_tallas)

        screen_equipamiento = Screen(name='equipamiento')
        screen_equipamiento.add_widget(EquipamientoScreen())
        sm.add_widget(screen_equipamiento)

        sm.current = 'login'

        return sm

if __name__ == '__main__':
    LoginApp().run()