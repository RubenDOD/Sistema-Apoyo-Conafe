from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from collections import OrderedDict
from utils.datatable_alumnosAsign import DataTableAlumnosAsign
from datetime import datetime
import hashlib
from db_connection import execute_non_query
from db_connection import execute_query
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

class AsignarAlumnosWindow(BoxLayout):
    #Builder.load_file("AsignarAlumno.kv")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cargar contenido inicial
        content = self.ids.scrn_contents
        users = self.get_users("General", 0)
        userstable = DataTableAlumnosAsign(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

    def reload_users(self):
        """Recarga la lista de usuarios en la pantalla principal."""
        content = self.ids.scrn_contents
        
        # Asegúrate de limpiar correctamente el contenido
        content.clear_widgets()

        # Verifica si obtienes nuevos datos
        print("Recargando usuarios desde la base de datos...")
        users = self.get_users("General", 0)
        print(f"Usuarios obtenidos: {users}")

        # Asegúrate de pasar datos actualizados
        userstable = DataTableAlumnosAsign(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, curp):
        """Callback para manejar acciones en la tabla."""
        print(f"CURP seleccionado: {curp}")
        self.ver_user(curp) 
        
    def get_unique_states(self):
        """Obtiene los estados únicos de la base de datos."""
        try:
            # Ejecutar consulta para obtener estados únicos
            sql = 'SELECT DISTINCT estado FROM CCT'
            result = execute_query(sql)

            # Convertir resultados a una lista
            states = [row[0] for row in result]

            return states

        except Exception as e:
            print(f"Error al obtener los estados: {e}")
            return []

    def ver_user(self, idx):
        """Muestra detalles básicos de un usuario específico basado en el CURP."""
        content = self.ids.scrn_view
        users = self.get_users("User", idx)
        user_info = {key: users[key][0] for key in users}

        # Nivel del alumno
        nivel_alumno = user_info['nivel']
        grado_alumno = user_info['grado']

        # Limpiar el contenido actual
        content.clear_widgets()

        # Crear un ScrollView para los detalles del usuario
        scroll_view = ScrollView(size_hint=(1, 1))
        user_info_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        user_info_layout.bind(minimum_height=user_info_layout.setter('height'))

        # Agregar los datos básicos del usuario
        user_info_layout.add_widget(Label(
            text=f"CURP: {user_info['CURP']}", 
            color=(0, 0, 0, 1), size_hint_y=None, height=50, 
            halign='left', valign='middle'
        ))
        user_info_layout.add_widget(Label(
            text=f"Nombre: {user_info['nombres']}", 
            color=(0, 0, 0, 1), size_hint_y=None, height=50, 
            halign='left', valign='middle'
        ))
        user_info_layout.add_widget(Label(
            text=f"Apellido Paterno: {user_info['apellido_paterno']}", 
            color=(0, 0, 0, 1), size_hint_y=None, height=50, 
            halign='left', valign='middle'
        ))
        user_info_layout.add_widget(Label(
            text=f"Nivel: {nivel_alumno}", 
            color=(0, 0, 0, 1), size_hint_y=None, height=50, 
            halign='left', valign='middle'
        ))
        user_info_layout.add_widget(Label(
            text=f"Grado: {grado_alumno}", 
            color=(0, 0, 0, 1), size_hint_y=None, height=50, 
            halign='left', valign='middle'
        ))
        # Crear un botón de regresar
        boton_regresar = Button(
            text="Regresar a la lista de alumnos",
            size_hint=(1, None),
            height=50
        )
        boton_regresar.bind(on_press=lambda instance: self.go_back_to_users())
        # Agregar el botón al layout
        user_info_layout.add_widget(boton_regresar)

        # Crear Spinners para Estado, CCT y Grupo
        unique_states = self.get_unique_states()
        spinner_estado = Spinner(
            text='Seleccionar Estado',
            values=unique_states,
            size_hint=(1, None),
            height=50
        )

        spinner_cct = Spinner(
            text="CCT",
            values=[],  # Vacío inicialmente
            size_hint=(1, None),
            height=50
        )

        spinner_grupo = Spinner(
            text="Grupo",
            values=[],  # Vacío inicialmente
            size_hint=(1, None),
            height=50
        )

        # Método para actualizar el segundo Spinner cuando cambie el primer Spinner
        def on_state_select(spinner, text):
            estado = text  # El texto seleccionado del Spinner
            capacitadores = self.get_ccts_estado(estado, nivel_alumno)  # Filtrar por nivel del alumno
            spinner_cct.values = capacitadores  # Actualiza los valores del segundo Spinner

        # Método para actualizar el tercer Spinner cuando cambie el segundo Spinner
        def on_cct_select(spinner, text, grado_alumno):
            cct = text.split()[0]  # Extraer la claveCentro del texto seleccionado
            grupos = self.get_grupos_cct(cct, grado_alumno)
            spinner_grupo.values = grupos  # Actualiza los valores del tercer Spinner

        # Vincular los eventos `text` de los Spinners
        spinner_estado.bind(text=on_state_select)
        spinner_cct.bind(text=lambda spinner, text: on_cct_select(spinner, text, grado_alumno))

        # Botón para asignar el CCT y Grupo al alumno
        def asignar_cct_grupo(instance):
            estado = spinner_estado.text
            cct = spinner_cct.text.split()[0] if spinner_cct.text != "CCT" else None
            grupo = spinner_grupo.text if spinner_grupo.text != "Grupo" else None

            # Validar que se hayan seleccionado Estado, CCT y Grupo
            if estado == "Seleccionar Estado" or not cct or not grupo:
                popup = Popup(
                    title="Error de Selección",
                    content=Label(
                        text="Por favor, seleccione un Estado, un CCT y un Grupo antes de continuar.",
                        halign="center"
                    ),
                    size_hint=(0.8, 0.4)
                )
                popup.open()
                return

            id_grupo = self.get_grupo_id(cct, grupo)  # Obtener el ID del grupo
            self.asignar_alumno_cct(idx, cct, id_grupo)  # Llamar a la función de inserción

        boton_asignar = Button(
            text="Asignar CCT y Grupo",
            size_hint=(1, None),
            height=50
        )
        boton_asignar.bind(on_press=asignar_cct_grupo)

        # Agregar los Spinners y el botón al layout
        user_info_layout.add_widget(spinner_estado)
        user_info_layout.add_widget(spinner_cct)
        user_info_layout.add_widget(spinner_grupo)
        user_info_layout.add_widget(boton_asignar)

        # Agregar el layout al ScrollView y al contenido
        scroll_view.add_widget(user_info_layout)
        content.add_widget(scroll_view)

        # Cambia a la pantalla de visualización de usuario
        self.ids.scrn_mngr.current = 'scrn_view'

    def get_grupo_id(self, cct, grupo):
        """Obtiene el ID del grupo basado en la claveCentro y el nombre del grupo."""
        try:
            # Consulta para obtener el ID del grupo
            sql = '''
                SELECT id_grupo FROM CCTgrupos
                WHERE id_CCT = ? AND nombre_grupo = ?
            '''
            result = execute_query(sql, (cct, grupo))

            return result[0][0] if result else None

        except Exception as e:
            print(f"Error al obtener el ID del grupo: {e}")
            return None

    def asignar_alumno_cct(self, id_alumno, id_cct, id_grupo):
        """Asigna un alumno a un CCT y grupo específico."""
        if not id_cct or not id_grupo:
            self.show_popup("Error", "CCT o grupo no seleccionados.")
            return

        try:
            # Inserción en la tabla alumnoCCT
            sql = '''
                INSERT INTO alumnoCCT (id_CCT, id_alumno, id_grupo)
                VALUES (?, ?, ?)
            '''
            execute_non_query(sql, (id_cct, id_alumno, id_grupo))

            # Consulta para obtener nivel y grado del grupo
            sql = '''
                SELECT nivel, grado FROM CCTgrupos WHERE id_grupo = ?
            '''
            result = execute_query(sql, (id_grupo,))

            if result:
                print(result)
                nivel, grado = result[0]

                # Determinar las materias según nivel y grado
                materias_sql = None
                if nivel in ["PRIMARIA", "Primaria"]:
                    if grado == '1':
                        materias_sql = '''
                            SELECT id_materia FROM Materias WHERE nombre_materia IN 
                            ('Español', 'Matemáticas', 'Exploración de la Naturaleza y la Sociedad', 
                            'Formación Cívica y Ética', 'Educación Artística');
                        '''
                    elif grado == '2':
                        materias_sql = '''
                            SELECT id_materia FROM Materias WHERE nombre_materia IN 
                            ('Español', 'Matemáticas', 'Ciencias Naturales', 
                            'La Entidad donde vivo', 'Formación Cívica y Ética', 'Educación Artística');
                        '''
                    elif grado == '3':
                        materias_sql = '''
                            SELECT id_materia FROM Materias WHERE nombre_materia IN 
                            ('Español', 'Matemáticas', 'Ciencias Naturales', 'Geografía', 
                            'Historia', 'Formación Cívica y Ética', 'Educación Artística');
                        '''
                elif nivel in ["SECUNDARIA", "Secundaria"]:
                    if grado == '1':
                        materias_sql = '''
                            SELECT id_materia FROM Materias WHERE nombre_materia IN 
                            ('Español', 'Matemáticas', 'Ciencias', 'Geografía', 'Educación Física');
                        '''
                    elif grado == '2':
                        materias_sql = '''
                            SELECT id_materia FROM Materias WHERE nombre_materia IN 
                            ('Español', 'Matemáticas', 'Ciencias', 'Historia', 'Formación Cívica y Ética', 'Educación Física');
                        '''
                    elif grado == '3':
                        materias_sql = '''
                            SELECT id_materia FROM Materias WHERE nombre_materia IN 
                            ('Español', 'Matemáticas', 'Ciencias', 'Historia', 'Formación Cívica y Ética', 'Educación Física');
                        '''

                if materias_sql:
                    materias = execute_query(materias_sql)
                    print(materias)
                    for materia in materias:
                        sql = '''
                            INSERT INTO calificaciones (id_alumno, id_materia, calificacion, fecha_registro)
                            VALUES (?, ?, ?, ?)
                        '''
                        fecha_actual = datetime.now()
                        execute_non_query(sql, (id_alumno, materia[0], 0.0, fecha_actual))

            # Mostrar mensaje de éxito
            self.show_popup("Éxito", "Alumno asignado correctamente.")
            self.reload_users()  # Recargar los usuarios no asignados
            self.go_back_to_convocatorias()

        except Exception as e:
            self.show_popup("Error", f"Ocurrió un error: {e}")

    def get_grupos_cct(self, cct, grado):
        """Obtiene los grupos disponibles para un CCT específico."""
        try:
            # Consulta para obtener grupos basados en el CCT seleccionado
            sql = '''
                SELECT nombre_grupo FROM CCTgrupos
                WHERE id_CCT = ? and grado = ?
            '''
            result = execute_query(sql, (cct, grado))

            # Formatear resultados para mostrarlos en el dropdown
            grupos = [nombre_grupo[0] for nombre_grupo in result]

            return grupos

        except Exception as e:
            print(f"Error al obtener los grupos: {e}")
            return []

    def get_ccts_estado(self, estado, nivel_alumno):
        """
        Obtiene los CCTs disponibles para un estado específico que coincidan con el nivel educativo del alumno.
        """
        try:
            # Consulta para obtener CCTs que coincidan con el estado y el nivel educativo
            sql = '''
                SELECT claveCentro, municipio, localidad 
                FROM CCT 
                WHERE estado = ? AND nivelEducativo = ?
            '''
            result = execute_query(sql, (estado, nivel_alumno))

            # Formatear resultados para mostrarlos en el dropdown
            ccts = [f"{claveCentro} {municipio} {localidad}" for claveCentro, municipio, localidad in result]

            return ccts

        except Exception as e:
            print(f"Error al obtener los CCTs: {e}")
            return []
        
    def go_back_to_convocatorias(self):
        """Regresa directamente a la pantalla 'vista_gestion_alumnos'."""
        try:
            app = App.get_running_app()  # Obtén la instancia de la aplicación principal
            app.root.current = 'vista_gestion_alumnos'  # Cambia la pantalla actual a 'vista_gestion_alumnos'
            print("Regresando a la pantalla 'vista_gestion_alumnos'")  # Solo para depuración
        except Exception as e:
            print(f"Error al regresar a la pantalla: {e}")

    # En el botón de regresar (cuando estás viendo los detalles del alumno)
    def go_back_button(self):
        """Manejo de regresar desde el detalle del alumno."""
        self.go_back_to_convocatorias()  # Usamos la función modificada

    def go_back_to_users(self):
        """Regresa a la pantalla principal desde el formulario."""
        self.ids.scrn_mngr.current = 'scrn_content'

    def show_popup(self, title, message):
        """Muestra un Popup con un mensaje."""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        popup.open()

    def get_users(self, mode, id):
        """Obtiene la lista de usuarios desde la base de datos."""
        if mode == "General":
            _alumnos = OrderedDict()
            _alumnos['CURP'] = {}
            _alumnos['nombres'] = {}
            _alumnos['apellido_paterno'] = {}
            _alumnos['nivel'] = {}

            # Consulta para obtener alumnos que no están en la tabla alumnoCCT
            sql = '''
                SELECT a.CURP, a.nombres, a.apellido_paterno, a.nivel
                FROM alumno a
                LEFT JOIN alumnoCCT ac ON a.CURP = ac.id_alumno
                WHERE ac.id_alumno IS NULL
            '''
            users = execute_query(sql)

            for idx, user in enumerate(users):
                _alumnos['CURP'][idx] = user[0]
                _alumnos['nombres'][idx] = user[1]
                _alumnos['apellido_paterno'][idx] = user[2]
                _alumnos['nivel'][idx] = user[3]

            return _alumnos

        else:  # Filtrar por CURP
            _alumnos = OrderedDict()
            _alumnos['CURP'] = {}
            _alumnos['nombres'] = {}
            _alumnos['apellido_paterno'] = {}
            _alumnos['nivel'] = {}
            _alumnos['grado'] = {}

            sql = 'SELECT * FROM alumno WHERE CURP = ?'
            users = execute_query(sql, (id,))

            for idx, user in enumerate(users):
                _alumnos['CURP'][idx] = user[0]
                _alumnos['nombres'][idx] = user[1]
                _alumnos['apellido_paterno'][idx] = user[2]
                _alumnos['nivel'][idx] = user[5]
                _alumnos['grado'][idx] = user[6]

            return _alumnos
        
class AsignarAlumnosApp(App):
    def build(self):
        return AsignarAlumnosWindow()

if __name__ == '__main__':
    AsignarAlumnosApp().run()