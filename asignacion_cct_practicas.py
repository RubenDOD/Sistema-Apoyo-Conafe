from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from functools import partial
import mysql.connector

#Builder.load_file('asignacion_cct_practicas.kv')  # Asegúrate de que el archivo tenga este nombre

class AsignacionCCTPracticasScreen(Screen):
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
            SELECT A.id_Aspirante, CONCAT(A.nombres, ' ', A.apellidoPaterno, ' ', A.apellidoMaterno) AS nombre_completo
            FROM Aspirante A
            LEFT JOIN AsignacionAspiranteCCT ACCT ON A.id_Aspirante = ACCT.id_Aspirante
            WHERE A.estado_solicitud = 'Finalizado' AND ACCT.id_Aspirante IS NULL;
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
        if not self.manager:
            print("Error: El ScreenManager no está configurado.")
            return
        print(f"Navegando al detalle de CCT para aspirante con ID: {aspirante_id}")
        detalle_screen = self.manager.get_screen("detalle_cct")
        detalle_screen.load_initial_ccts(aspirante_id)
        self.manager.current = "detalle_cct"

    def go_back(self):
        if self.manager:
            print("Regresando a VistaDireccionTerritorialScreen...")
            self.manager.current = "vista_direccion_territorial"
        else:
            print("Error: El ScreenManager no está configurado.")

class DetalleCCTScreen(Screen):
    def load_initial_ccts(self, aspirante_id):
        self.aspirante_id = aspirante_id
        print(f"Cargando CCT iniciales para aspirante con ID: {aspirante_id}...")  # Debug
        try:
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            cursor = db.cursor()

            # Obtener ubicación, nivel educativo y datos del aspirante
            query_aspirante = """
            SELECT ResidenciaAspirante.estado, ResidenciaAspirante.municipio, InfoEducativaAspirante.nivelEducativo,
                CONCAT(Aspirante.nombres, ' ', Aspirante.apellidoPaterno, ' ', Aspirante.apellidoMaterno) AS nombre_completo
            FROM ResidenciaAspirante
            JOIN InfoEducativaAspirante ON ResidenciaAspirante.id_Aspirante = InfoEducativaAspirante.id_Aspirante
            JOIN Aspirante ON ResidenciaAspirante.id_Aspirante = Aspirante.id_Aspirante
            WHERE ResidenciaAspirante.id_Aspirante = %s;
            """
            cursor.execute(query_aspirante, (aspirante_id,))
            aspirante_data = cursor.fetchone()

            if not aspirante_data:
                print("No se encontraron datos del aspirante.")  # Debug
                return

            estado, municipio, nivel_educativo, nombre_completo = aspirante_data
            print(f"Ubicación: {estado}, {municipio}, Nivel Educativo: {nivel_educativo}, Nombre: {nombre_completo}")  # Debug

            self.ids.aspirante_info.text = (
                f"Datos del Aspirante:\n"
                f"Nombre: {nombre_completo}\n"
                f"Estado: {estado}\n"
                f"Municipio: {municipio}\n"
                f"Nivel Educativo: {nivel_educativo}"
            )
            self.estado_aspirante = estado
            self.municipio_aspirante = municipio
            self.nivel_educativo = nivel_educativo

            # Buscar CCT iniciales
            query_ccts = """
            SELECT claveCentro, nombre, estado, municipio, nivelEducativo, cupos_disponibles
            FROM CCT
            WHERE estado = %s AND municipio = %s AND nivelEducativo = %s AND cupos_disponibles > 0
            ORDER BY estado, municipio;
            """
            cursor.execute(query_ccts, (estado, municipio, nivel_educativo))
            ccts = cursor.fetchall()
            db.close()

            print("CCT iniciales recuperados:", ccts)  # Debug

            # Mostrar resultados iniciales
            self.ids.cct_list.clear_widgets()
            for cct in ccts:
                # Crear fila para cada CCT
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

                # Añadir la fila al layout principal
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
            db.commit()
            db.close()

            print("CCT asignado correctamente.")  # Debug

            # Redirigir al usuario al AsignacionCCTPracticasScreen y recargar los datos
            self.manager.current = "main"
            self.manager.get_screen("main").load_data()
        except mysql.connector.Error as err:
            print(f"Error al asignar CCT: {err}")

    def reload_ccts(self, *args):
        # Recarga la lista inicial de CCTs
        self.load_initial_ccts(self.aspirante_id)

    def go_back(self):
        """Regresa al AsignacionCCTPracticasScreen"""
        if self.manager:
            print("Regresando a AsignacionCCTPracticasScreen...")
            self.manager.current = "cct_capacitaciones"
        else:
            print("Error: ScreenManager no está configurado.")

class AsignacionCCTApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AsignacionCCTPracticasScreen(name="asignacion_cct_practicas"))
        sm.add_widget(DetalleCCTScreen(name="detalle_cct"))
        return sm
    
if __name__ == "__main__":
    AsignacionCCTApp().run()