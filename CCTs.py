from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from collections import OrderedDict
from utils.datatable_ccts import DataTableCCTs
from datetime import datetime
import hashlib
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

class CCTsWindow(BoxLayout):
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
        userstable = DataTableCCTs(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

    def reload_users(self):
        """Recarga la lista de usuarios en la pantalla principal."""
        content = self.ids.scrn_contents
        
        # Asegúrate de limpiar correctamente el contenido
        content.clear_widgets()

        # Verifica si obtienes nuevos datos
        print("Recargando usuarios desde la base de datos...")
        users = self.get_users("General", 0)
        

        # Asegúrate de pasar datos actualizados
        userstable = DataTableCCTs(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, btn_text, user_id):
        """Callback para manejar acciones en la tabla."""
        print(f"Texto del botón: {btn_text}, ID del usuario: {user_id}")
        self.ver_user(user_id)  # Usar el user_id para mostrar detalles
        
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

    def ver_user(self, id_cct):
        """Muestra detalles básicos de un CCT específico basado en su clave."""
        content = self.ids.scrn_view

        # Consulta para obtener detalles del CCT
        try:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            mycursor = mydb.cursor()

            # Consulta para obtener información básica del CCT
            sql_cct = '''
                SELECT claveCentro, estado, municipio, nivelEducativo
                FROM CCT
                WHERE claveCentro = %s
            '''
            mycursor.execute(sql_cct, (id_cct,))
            cct_info = mycursor.fetchone()

            # Consulta para obtener los grupos asociados al CCT
            sql_grupos = '''
                SELECT id_grupo, nombre_grupo, nivel, grado
                FROM CCTgrupos
                WHERE id_CCT = %s
            '''
            mycursor.execute(sql_grupos, (id_cct,))
            grupos = mycursor.fetchall()

        finally:
            mycursor.close()
            mydb.close()

        # Limpiar el contenido actual
        content.clear_widgets()

        # Crear un ScrollView para los detalles del CCT
        scroll_view = ScrollView(size_hint=(1, 1))
        cct_info_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        cct_info_layout.bind(minimum_height=cct_info_layout.setter('height'))

        # Mostrar información básica del CCT
        if cct_info:
            cct_info_layout.add_widget(Label(
                text=f"Clave Centro: {cct_info[0]}", color=(0, 0, 0, 1), size_hint_y=None, height=50))
            cct_info_layout.add_widget(Label(
                text=f"Estado: {cct_info[1]}", color=(0, 0, 0, 1), size_hint_y=None, height=50))
            cct_info_layout.add_widget(Label(
                text=f"Municipio: {cct_info[2]}", color=(0, 0, 0, 1), size_hint_y=None, height=50))
            cct_info_layout.add_widget(Label(
                text=f"Nivel Educativo: {cct_info[3]}", color=(0, 0, 0, 1), size_hint_y=None, height=50))
        else:
            cct_info_layout.add_widget(Label(
                text="CCT no encontrado", color=(0, 0, 0, 1), size_hint_y=None, height=50))

        # Mostrar grupos asociados
        cct_info_layout.add_widget(Label(
            text="Grupos Asociados:", color=(0, 0, 0, 1), size_hint_y=None, height=50))

        if grupos:
            for grupo in grupos:
                cct_info_layout.add_widget(Label(
                    text=f"{grupo[2]} Nivel {grupo[3]} - Nombre: {grupo[1]}", color=(0, 0, 0, 1), size_hint_y=None, height=50))
        else:
            cct_info_layout.add_widget(Label(
                text="No hay grupos asociados a este CCT.", color=(0, 0, 0, 1), size_hint_y=None, height=50))

        # Botón para cambiar a la pantalla de añadir grupo
        enable_button = Button(text="Nuevo Grupo", size_hint_y=None, height=50)

        def switch_to_add_group(instance):
            # Guarda el ID del CCT actual en un atributo
            self.current_cct = id_cct
            self.ids.scrn_mngr.current = 'scrn_add_group'

        enable_button.bind(on_release=switch_to_add_group)

        # Agregar el botón al layout
        cct_info_layout.add_widget(enable_button)

        # Agregar el layout al ScrollView y al contenido
        scroll_view.add_widget(cct_info_layout)
        content.add_widget(scroll_view)

        # Cambiar a la pantalla de visualización de CCT
        self.ids.scrn_mngr.current = 'scrn_view'



    def add_group_to_cct(self, id_cct, group_name, grade):
        """Añade un grupo a un CCT en la base de datos y muestra un mensaje de confirmación."""
        if not group_name.strip():
            self.show_popup("Error", "El nombre del grupo no puede estar vacío.")
            return

        if grade == "Seleccionar Grado":
            self.show_popup("Error", "Debes seleccionar un nivel y un grado.")
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
            sql = '''
                SELECT nivelEducativo FROM CCT WHERE 
                claveCentro = %s
            '''
            mycursor.execute(sql, (id_cct,))
            nivelEducativo = mycursor.fetchall()
            nivel = nivelEducativo[0][0] 
            # Insertar grupo en la tabla CCTgrupos
            sql = '''
                INSERT INTO CCTgrupos (id_CCT, nombre_grupo, nivel, grado)
                VALUES (%s, %s, %s, %s)
            '''
            mycursor.execute(sql, (id_cct, group_name, nivel, grade))
            mydb.commit()

            # Mostrar mensaje de éxito
            self.show_popup("Éxito", f"Grupo '{group_name}' añadido correctamente al CCT {id_cct}.")

        except mysql.connector.Error as err:
            # Manejar errores de la base de datos
            self.show_popup("Error", f"No se pudo añadir el grupo: {err}")

        finally:
            # Cerrar conexión
            mycursor.close()
            mydb.close()







    def get_grupo_id(self, cct, grupo):
        """Obtiene el ID del grupo basado en la claveCentro y el nombre del grupo."""
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

        mycursor.close()
        mydb.close()

        return result[0] if result else None


    def asignar_alumno_cct(self, id_alumno, id_cct, id_grupo):
        """Asigna un alumno a un CCT y grupo específico."""
        if not id_cct or not id_grupo:
            self.show_popup("Error", "CCT o grupo no seleccionados.")
            return

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
        try:
            mycursor.execute(sql, (id_cct, id_alumno, id_grupo))
            mydb.commit()

            # Muestra un popup de éxito
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



    def get_ccts_estado(self, estado):
        # Conectar a la base de datos y obtener capacitadores para el CCT seleccionado
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        # Consulta para obtener nombres de capacitadores asignados a un CCT específico
        sql = '''
            SELECT  claveCentro, municipio, localidad FROM CCT
            WHERE estado = %s
        '''
        mycursor.execute(sql, (estado,))
        result = mycursor.fetchall()

        # Formatear resultados para mostrarlos en el dropdown
        ccts = [f"{claveCentro} {municipio} {localidad}" for claveCentro, municipio, localidad in result]

        mycursor.close()
        mydb.close()

        return ccts
    
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
                _ccts = OrderedDict()
                _ccts['claveCentro'] = {}
                _ccts['estado'] = {}
                _ccts['municipio'] = {}
                _ccts['nivelEducativo'] = {}
                ids = []
                estados = []
                municipios = []
                niveles = []

                # Consulta para obtener alumnos que no están en la tabla alumnoCCT
                sql = '''
                    SELECT claveCentro, estado, municipio, nivelEducativo
                    FROM CCT
                '''
                mycursor.execute(sql)

                users = mycursor.fetchall()
                for user in users:
                    ids.append(user[0])  # Clave
                    estados.append(user[1])  
                    municipios.append(user[2])
                    niveles.append(user[3])  # Nivel

                users_length = len(ids)
                idx = 0
                while idx < users_length:
                    _ccts['claveCentro'][idx] = ids[idx]
                    _ccts['estado'][idx] = estados[idx]
                    _ccts['municipio'][idx] = municipios[idx]
                    _ccts['nivelEducativo'][idx] = niveles[idx]
                    idx += 1

                return _ccts

            else:  # Filtrar por CURP
                _ccts = OrderedDict()
                _ccts['CURP'] = {}
                _ccts['nombres'] = {}
                _ccts['apellido_paterno'] = {}
                _ccts['nivel'] = {}

                sql = 'SELECT * FROM alumno WHERE CURP = %s'
                mycursor.execute(sql, (id,))
                users = mycursor.fetchall()

                for idx, user in enumerate(users):
                    _ccts['CURP'][idx] = user[0]
                    _ccts['nombres'][idx] = user[1]
                    _ccts['apellido_paterno'][idx] = user[2]
                    _ccts['nivel'][idx] = user[5]

                return _ccts
        finally:
            # Cierra el cursor y la conexión
            mycursor.close()
            mydb.close()

        


class CCTsApp(App):
    def build(self):
        return CCTsWindow()


if __name__ == '__main__':
    CCTsApp().run()