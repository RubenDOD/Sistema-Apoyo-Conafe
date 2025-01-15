from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.lang import Builder
from db_connection import execute_query_comb  # Función para ejecutar consultas

# Carga explícita del archivo KV
Builder.load_file('PromocionEscolar.kv')

class PromocionScreen(BoxLayout):
    def go_back_to_convocatorias(self):
        """Regresa a la pantalla principal."""
        try:
            app = App.get_running_app()  # Obtén la instancia de la aplicación principal
            app.root.current = "vista_gestion_alumnos"  # Cambia a la pantalla específica
            print("Regresando a la pantalla 'vista_gestion_alumnos'")
        except Exception as e:
            print(f"Error al regresar a la pantalla: {e}")

    def on_kv_post(self, base_widget):
        # Inicializa el listado de niveles
        nivel_spinner = self.ids.nivel_spinner
        nivel_spinner.values = ['Primaria', 'Secundaria', 'Certificado']  # Niveles disponibles

    def actualizar_alumnos_por_nivel(self, nivel):
        # Obtiene los alumnos del nivel seleccionado desde la base de datos
        query = """
            SELECT CURP, nombres + ' ' + apellido_paterno + ' ' + apellido_materno AS nombre_completo, grado, nivel
            FROM alumno
            WHERE nivel = ?;
        """
        alumnos = execute_query_comb(query, (nivel,))

        spinner = self.ids.alumno_spinner
        spinner.values = [row[1] for row in alumnos]  # Nombres de los alumnos
        self.alumnos = {row[1]: {'curp': row[0], 'grado': row[2], 'nivel': row[3]} for row in alumnos}  # Datos mapeados

        # Limpia las calificaciones al cambiar de nivel
        self.ids.table_layout.clear_widgets()

    def mostrar_calificaciones(self, alumno_nombre):
        # Obtén el CURP, grado y nivel del alumno seleccionado
        alumno_data = self.alumnos.get(alumno_nombre)
        if not alumno_data:
            return

        alumno_curp = alumno_data['curp']
        alumno_grado = alumno_data['grado']
        alumno_nivel = alumno_data['nivel']

        # Limpia los datos anteriores
        table_layout = self.ids.table_layout
        table_layout.clear_widgets()

        # Muestra el grado y nivel del alumno
        table_layout.add_widget(Label(text='Grado:', bold=True, size_hint_y=None, height=40))
        table_layout.add_widget(Label(text=str(alumno_grado), size_hint_y=None, height=40))
        table_layout.add_widget(Label(text='Nivel:', bold=True, size_hint_y=None, height=40))
        table_layout.add_widget(Label(text=str(alumno_nivel), size_hint_y=None, height=40))

        # Agrega espacio entre grado/nivel y las calificaciones
        table_layout.add_widget(Label(text='', size_hint_y=None, height=20))
        table_layout.add_widget(Label(text='', size_hint_y=None, height=20))

        # Obtén las calificaciones del alumno desde la base de datos
        query = """
            SELECT m.nombre_materia, c.calificacion
            FROM calificaciones c
            JOIN materias m ON c.id_materia = m.id_materia
            WHERE c.id_alumno = ?;
        """
        calificaciones = execute_query_comb(query, (alumno_curp,))

        # Agrega encabezados para la tabla de calificaciones
        table_layout.add_widget(Label(text='Materia', bold=True, size_hint_y=None, height=40))
        table_layout.add_widget(Label(text='Calificación', bold=True, size_hint_y=None, height=40))

        # Agrega filas de calificaciones
        self.calificaciones_actuales = []  # Guardar calificaciones para verificar después
        for cal in calificaciones:
            table_layout.add_widget(Label(text=cal[0], size_hint_y=None, height=40))  # Nombre de la materia
            table_layout.add_widget(Label(text=str(cal[1]), size_hint_y=None, height=40))  # Calificación
            self.calificaciones_actuales.append(cal[1])

    def promover_alumno(self):
        alumno_nombre = self.ids.alumno_spinner.text
        if alumno_nombre == "Selecciona un alumno":
            self.mostrar_popup("Error", "Por favor selecciona un alumno.")
            return

        alumno_data = self.alumnos.get(alumno_nombre)
        if not alumno_data:
            self.mostrar_popup("Error", "No se encontraron datos del alumno.")
            return

        # Verifica si hay calificaciones menores a 60
        if any(cal < 6 for cal in self.calificaciones_actuales):
            self.mostrar_popup("Error", "El alumno no puede ser promovido debido a calificaciones menores a 6.")
            return

        # Actualiza el grado y nivel del alumno
        nuevo_grado = alumno_data['grado'] + 1
        nuevo_nivel = alumno_data['nivel']

        if alumno_data['grado'] == 3:  # Promoción al siguiente nivel
            if alumno_data['nivel'] == "Primaria":
                nuevo_nivel = "Secundaria"  # Primaria -> Secundaria
            elif alumno_data['nivel'] == "Secundaria":
                nuevo_nivel = "Certificado"  # Secundaria -> Certificado
            nuevo_grado = 1  # Reinicia el grado

        # Elimina las materias asociadas al alumno en cualquier promoción
        delete_query = """
            DELETE FROM calificaciones
            WHERE id_alumno = ?;
        """

        delete_query_2 = """
            UPDATE alumnoCCT SET id_grupo = NULL
            WHERE id_alumno = ?;
        """
        try:
            execute_query_comb(delete_query, (alumno_data['curp'],))
            execute_query_comb(delete_query_2, (alumno_data['curp'],))

            print(f"Calificaciones del alumno {alumno_data['curp']} eliminadas exitosamente.")
        except Exception as e:
            print(f"Error al eliminar calificaciones: {e}")
            self.mostrar_popup("Error", "Hubo un problema al restablecer las calificaciones del alumno.")
            return

        # Debug: Verifica los valores antes de actualizar
        print(f"Promoviendo alumno: {alumno_data['curp']}, Nuevo Grado: {nuevo_grado}, Nuevo Nivel: {nuevo_nivel}")

        # Actualiza el grado y nivel en la base de datos
        update_query = """
            UPDATE alumno
            SET grado = ?, nivel = ?
            WHERE CURP = ?;
        """
        try:
            execute_query_comb(update_query, (nuevo_grado, nuevo_nivel, alumno_data['curp']))
            self.mostrar_popup("Éxito", "El alumno ha sido promovido correctamente.")
            # Actualizar la lista de alumnos después del cambio
            self.actualizar_alumnos_por_nivel(str(nuevo_nivel))
        except Exception as e:
            print(f"Error al promover al alumno: {e}")
            self.mostrar_popup("Error", "Hubo un problema al promover al alumno.")

    def mostrar_popup(self, titulo, mensaje):
        popup = Popup(title=titulo, content=Label(text=mensaje), size_hint=(0.6, 0.4))
        popup.open()

    def actualizar_datos(self):
        # Obtiene el nivel seleccionado
        nivel_seleccionado = self.ids.nivel_spinner.text
        if nivel_seleccionado == "Selecciona un nivel":
            self.mostrar_popup("Error", "Por favor selecciona un nivel.")
            return

        # Refresca la lista de alumnos
        self.actualizar_alumnos_por_nivel(nivel_seleccionado)

        # Si hay un alumno seleccionado, refresca sus calificaciones
        alumno_seleccionado = self.ids.alumno_spinner.text
        if alumno_seleccionado != "Selecciona un alumno":
            self.mostrar_calificaciones(alumno_seleccionado)
class CalificacionesApp(App):
    def build(self):
        return PromocionScreen()


if __name__ == "__main__":
    CalificacionesApp().run()
