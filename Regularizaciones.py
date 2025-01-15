from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from db_connection import execute_query
from db_connection import execute_non_query
from datetime import datetime
from pytz import timezone

class Regularizaciones(BoxLayout):
    def __init__(self, cct=None, grupo=None, **kwargs):
        super(Regularizaciones, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.cct = cct
        self.grupo = grupo

        # Contenedor para los alumnos
        self.scroll = ScrollView(size_hint=(1, 1))
        self.records_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        self.records_layout.bind(minimum_height=self.records_layout.setter("height"))
        self.scroll.add_widget(self.records_layout)
        self.add_widget(self.scroll)

        # Cargar los alumnos al iniciar la app
        self.load_alumnos()

        # Botón de regresar
        self.regresar_button = Button(
            text="Regresar", size_hint_y=None, height=50
        )
        self.regresar_button.bind(on_press=self.regresar)
        self.add_widget(self.regresar_button)

    def load_alumnos(self):
        """Carga los alumnos desde la base de datos."""
        query = """
        SELECT 
            a.CURP, 
            CONCAT(a.apellido_paterno, ' ', a.apellido_materno, ' ', a.nombres) AS nombre_completo,
            COUNT(c.id_materia) AS materias_reprobadas
        FROM 
            alumno a
        JOIN 
            alumnoCCT ac ON a.CURP = ac.id_alumno
        JOIN 
            CCTgrupos cg ON ac.id_grupo = cg.id_grupo
        JOIN
            Calificaciones c ON c.id_alumno = a.CURP
        WHERE 
            ac.id_CCT = ? AND cg.nombre_grupo = ?
            AND c.calificacion < 6
        GROUP BY
            a.CURP, a.apellido_paterno, a.apellido_materno, a.nombres
        """
        try:
            rows = execute_query(query, (self.cct, self.grupo))
            print(rows)
            if rows:
                for row in rows:
                    curp, nombre_completo = row[0], row[1]
                    alumno_button = Button(
                        text=nombre_completo,
                        size_hint_y=None,
                        height=50,
                    )
                    # Asocia un evento para abrir la ventana de calificaciones
                    alumno_button.bind(on_press=lambda instance, curp=curp: self.show_details(curp))
                    self.records_layout.add_widget(alumno_button)
            else:
                self.records_layout.add_widget(Label(text="No hay alumnos con calificaciones menores a 6."))
        except Exception as e:
            self.show_error(f"Error obteniendo alumnos: {e}")

    def show_details(self, curp):
        """Muestra las calificaciones del alumno en un popup."""
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Título de la ventana
        popup_layout.add_widget(Label(text=f"Calificaciones del alumno {curp}", size_hint_y=None, height=40))

        # Contenedor de calificaciones en formato tabla
        scroll = ScrollView(size_hint=(1, 1))
        table_layout = GridLayout(cols=4, size_hint_y=None, spacing=5, padding=5)
        table_layout.bind(minimum_height=table_layout.setter("height"))
        scroll.add_widget(table_layout)
        popup_layout.add_widget(scroll)

        # Encabezados de la tabla
        table_layout.add_widget(Label(text="Materia", bold=True, size_hint_y=None, height=30))
        table_layout.add_widget(Label(text="Calificación", bold=True, size_hint_y=None, height=30))
        table_layout.add_widget(Label(text="Fecha", bold=True, size_hint_y=None, height=30))
        table_layout.add_widget(Label(text="Actualizar", bold=True, size_hint_y=None, height=30))

        # Variable para calcular el promedio
        total_calificaciones = 0
        num_calificaciones = 0

        # Cargar las calificaciones del alumno
        query = """
        SELECT c.id_calificacion, m.nombre_materia, c.calificacion, c.fecha_registro
        FROM Calificaciones c
        JOIN Materias m ON c.id_materia = m.id_materia
        WHERE c.id_alumno = ? AND c.calificacion < 6
        """
        try:
            rows = execute_query(query, (curp,))
            print(f'Calificaciones: {rows}')
            if rows:
                for row in rows:
                    id_calificacion, materia, calificacion, fecha = row
                    # Convertir Decimal a str y formatear el datetime
                    calificacion_str = str(calificacion)  # Convertir Decimal a string si es necesario
                    fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')  # Formatear la fecha a string
                    table_layout.add_widget(Label(text=materia, size_hint_y=None, height=30))
                    table_layout.add_widget(Label(text=calificacion_str, size_hint_y=None, height=30))
                    table_layout.add_widget(Label(text=fecha_str, size_hint_y=None, height=30))

                    # Botón para actualizar calificación
                    update_button = Button(text="Actualizar", size_hint_y=None, height=30)
                    update_button.bind(
                        on_press=lambda instance, id_c=id_calificacion, curr_cal=calificacion: self.update_calificacion_popup(
                            id_c, curr_cal
                        )
                    )
                    table_layout.add_widget(update_button)

                    # Acumular para el cálculo del promedio
                    total_calificaciones += calificacion
                    num_calificaciones += 1
            else:
                table_layout.add_widget(Label(text="No hay calificaciones menores a 6.", size_hint_y=None, height=30))
        except Exception as e:
            table_layout.add_widget(Label(text=f"Error: {e}", size_hint_y=None, height=30))

        # Calcular promedio
        promedio = total_calificaciones / num_calificaciones if num_calificaciones > 0 else 0

        # Mostrar el promedio
        popup_layout.add_widget(Label(text=f"Promedio Final: {promedio:.2f}", size_hint_y=None, height=40))

        # Botón de cerrar
        close_button = Button(text="Cerrar", size_hint_y=None, height=50)
        close_button.bind(on_press=lambda instance: popup.dismiss())
        popup_layout.add_widget(close_button)

        # Mostrar el popup
        popup = Popup(
            title="Detalles del Alumno",
            content=popup_layout,
            size_hint=(0.9, 0.9),
        )
        popup.open()

    def update_calificacion_popup(self, id_calificacion, current_calificacion):
        """Ventana emergente para ingresar nueva calificación."""
        update_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Mensaje informativo
        update_layout.add_widget(Label(text=f"Actualizar Calificación (ID: {id_calificacion})", size_hint_y=None, height=40))
        update_layout.add_widget(Label(text=f"Calificación Actual: {current_calificacion}", size_hint_y=None, height=30))

        # Campo para ingresar nueva calificación
        new_cal_input = TextInput(hint_text="Nueva Calificación (Ej: 85.5)", multiline=False, size_hint_y=None, height=40)
        update_layout.add_widget(new_cal_input)

        # Botón de actualizar
        update_button = Button(text="Actualizar", size_hint_y=None, height=50)
        update_button.bind(on_press=lambda instance: self.update_calificacion(id_calificacion, new_cal_input.text))
        update_layout.add_widget(update_button)

        # Botón de cancelar
        cancel_button = Button(text="Cancelar", size_hint_y=None, height=50)
        update_layout.add_widget(cancel_button)

        # Mostrar el popup
        popup = Popup(
            title="Actualizar Calificación",
            content=update_layout,
            size_hint=(0.8, 0.5),
        )
        cancel_button.bind(on_press=popup.dismiss)
        update_button.bind(on_press=lambda instance: popup.dismiss())
        popup.open()

    def update_calificacion(self, id_calificacion, nueva_calificacion):
        """Actualiza la calificación en la base de datos."""
        try:
            nueva_calificacion = float(nueva_calificacion)
        except ValueError:
            self.show_error("Por favor, ingresa un valor válido.")
            return

        tz = timezone('America/Mexico_City')
        current_time = datetime.now(tz)
        # Conectar a la base de datos y actualizar calificación
        query = "UPDATE Calificaciones SET calificacion = ?, fecha_registro = ? WHERE id_calificacion = ?"
        try:
            execute_non_query(query, (nueva_calificacion,current_time, id_calificacion))
            self.show_error(f"Calificación actualizada correctamente a {nueva_calificacion}.")
        except Exception as e:
            self.show_error(f"Error actualizando calificación: {e}")

    def show_error(self, message):
        """Mostrar error en un popup."""
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message, size_hint_y=None, height=40))
        close_button = Button(text="Cerrar", size_hint_y=None, height=50)
        popup_layout.add_widget(close_button)

        popup = Popup(
            title="Mensaje",
            content=popup_layout,
            size_hint=(0.8, 0.3),
        )
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def regresar(self, instance):
        """Regresa a la pantalla anterior."""
        app = App.get_running_app()
        app.root.current = 'lec'  # Cambia por el nombre de la pantalla anterior


class RegularizacionesApp(App):
    def build(self):
        return Regularizaciones()

if __name__ == "__main__":
    RegularizacionesApp().run()
