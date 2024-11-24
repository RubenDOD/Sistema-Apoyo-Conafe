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
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

class AsignarAlumnosWindow(BoxLayout):
    Builder.load_file("AsignarAlumno.kv")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Conexión a la base de datos
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        self.mycursor = self.mydb.cursor()

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
            # Conexión a la base de datos
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            mycursor = mydb.cursor()

            # Ejecutar consulta para obtener estados únicos
            sql = 'SELECT DISTINCT estado FROM CCT'
            mycursor.execute(sql)
            result = mycursor.fetchall()

            # Convertir resultados a una lista
            states = [row[0] for row in result]

            mycursor.close()
            mydb.close()
            return states

        except mysql.connector.Error as e:
            print(f"Error al obtener los estados: {e}")
            return []

    def ver_user(self, idx):
        """Muestra detalles básicos de un usuario específico basado en el CURP."""
        content = self.ids.scrn_view
        users = self.get_users("User", idx)
        user_info = {key: users[key][0] for key in users}

        # Nivel del alumno
        nivel_alumno = user_info['nivel']

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
        def on_cct_select(spinner, text):
            cct = text.split()[0]  # Extraer la claveCentro del texto seleccionado
            grupos = self.get_grupos_cct(cct)
            spinner_grupo.values = grupos  # Actualiza los valores del tercer Spinner

        # Vincular los eventos `text` de los Spinners
        spinner_estado.bind(text=on_state_select)
        spinner_cct.bind(text=on_cct_select)

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
            # Conexión a la base de datos
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            mycursor = mydb.cursor()

            # Consulta para obtener el ID del grupo
            sql = '''
                SELECT id_grupo FROM CCTgrupos
                WHERE id_CCT = %s AND nombre_grupo = %s
            '''
            mycursor.execute(sql, (cct, grupo))
            result = mycursor.fetchone()

            return result[0] if result else None

        except mysql.connector.Error as e:
            print(f"Error al obtener el ID del grupo: {e}")
            return None

        finally:
            mycursor.close()
            mydb.close()


    def asignar_alumno_cct(self, id_alumno, id_cct, id_grupo):
        """Asigna un alumno a un CCT y grupo específico."""
        if not id_cct or not id_grupo:
            self.show_popup("Error", "CCT o grupo no seleccionados.")
            return

        try:
            # Conexión a la base de datos
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            mycursor = mydb.cursor()

            # Inserción en la tabla alumnoCCT
            sql = '''
                INSERT INTO alumnoCCT (id_CCT, id_alumno, id_grupo)
                VALUES (%s, %s, %s)
            '''
            mycursor.execute(sql, (id_cct, id_alumno, id_grupo))
            mydb.commit()

            # Mostrar mensaje de éxito
            self.show_popup("Éxito", "Alumno asignado correctamente.")
            self.reload_users()  # Recargar los usuarios no asignados
            self.go_back_to_convocatorias()

        except mysql.connector.Error as err:
            self.show_popup("Error", f"Ocurrió un error: {err}")
        finally:
            mycursor.close()
            mydb.close()


    def get_grupos_cct(self, cct):
        """Obtiene los grupos disponibles para un CCT específico."""
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        # Consulta para obtener grupos basados en el CCT seleccionado
        sql = '''
            SELECT nombre_grupo FROM CCTgrupos
            WHERE id_CCT = %s
        '''
        mycursor.execute(sql, (cct,))
        result = mycursor.fetchall()

        # Formatear resultados para mostrarlos en el dropdown
        grupos = [nombre_grupo[0] for nombre_grupo in result]

        mycursor.close()
        mydb.close()

        return grupos



    def get_ccts_estado(self, estado, nivel_alumno):
        """
        Obtiene los CCTs disponibles para un estado específico que coincidan con el nivel educativo del alumno.
        """
        try:
            # Conexión a la base de datos
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            mycursor = mydb.cursor()

            # Consulta para obtener CCTs que coincidan con el estado y el nivel educativo
            sql = '''
                SELECT claveCentro, municipio, localidad 
                FROM CCT 
                WHERE estado = %s AND nivelEducativo = %s
            '''
            mycursor.execute(sql, (estado, nivel_alumno))
            result = mycursor.fetchall()

            # Formatear resultados para mostrarlos en el dropdown
            ccts = [f"{claveCentro} {municipio} {localidad}" for claveCentro, municipio, localidad in result]

            return ccts

        except mysql.connector.Error as e:
            print(f"Error al obtener los CCTs: {e}")
            return []

        finally:
            mycursor.close()
            mydb.close()

    
    def go_back_to_convocatorias(self):
        """Regresa a la pantalla principal."""
        self.reload_users()
        self.ids.scrn_mngr.current = 'scrn_content'
        self.reload_users()


    def show_popup(self, title, message):
        """Muestra un Popup con un mensaje."""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        popup.open()


    def go_back_to_users(self):
        """Regresa a la pantalla principal desde el formulario."""
        self.ids.scrn_mngr.current = 'scrn_content'

    def get_users(self, mode, id):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()
        
        try:
            """Obtiene la lista de usuarios desde la base de datos."""
            if mode == "General":
                _alumnos = OrderedDict()
                _alumnos['CURP'] = {}
                _alumnos['nombres'] = {}
                _alumnos['apellido_paterno'] = {}
                _alumnos['nivel'] = {}
                ids = []
                nombres = []
                apellidos = []
                niveles = []

                # Consulta para obtener alumnos que no están en la tabla alumnoCCT
                sql = '''
                    SELECT a.CURP, a.nombres, a.apellido_paterno, a.nivel
                    FROM alumno a
                    LEFT JOIN alumnoCCT ac ON a.CURP = ac.id_alumno
                    WHERE ac.id_alumno IS NULL
                '''
                mycursor.execute(sql)

                users = mycursor.fetchall()
                for user in users:
                    ids.append(user[0])  # CURP
                    nombres.append(user[1])  # Nombres
                    apellidos.append(user[2])  # Apellido paterno
                    niveles.append(user[3])  # Nivel

                users_length = len(nombres)
                idx = 0
                while idx < users_length:
                    _alumnos['CURP'][idx] = ids[idx]
                    _alumnos['nombres'][idx] = nombres[idx]
                    _alumnos['apellido_paterno'][idx] = apellidos[idx]
                    _alumnos['nivel'][idx] = niveles[idx]
                    idx += 1

                return _alumnos

            else:  # Filtrar por CURP
                _alumnos = OrderedDict()
                _alumnos['CURP'] = {}
                _alumnos['nombres'] = {}
                _alumnos['apellido_paterno'] = {}
                _alumnos['nivel'] = {}

                sql = 'SELECT * FROM alumno WHERE CURP = %s'
                mycursor.execute(sql, (id,))
                users = mycursor.fetchall()

                for idx, user in enumerate(users):
                    _alumnos['CURP'][idx] = user[0]
                    _alumnos['nombres'][idx] = user[1]
                    _alumnos['apellido_paterno'][idx] = user[2]
                    _alumnos['nivel'][idx] = user[5]

                return _alumnos
        finally:
            # Cierra el cursor y la conexión
            mycursor.close()
            mydb.close()

        


class AsignarAlumnosApp(App):
    def build(self):
        return AsignarAlumnosWindow()


if __name__ == '__main__':
    AsignarAlumnosApp().run()