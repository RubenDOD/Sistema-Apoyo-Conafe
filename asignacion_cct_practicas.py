from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from functools import partial
import mysql.connector


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Inicializando MainScreen...")  # Debug

    def on_kv_post(self, base_widget):
        print("Cargando DataTableAsignacionCCT en MainScreen...")  # Debug
        self.load_data()

    def load_data(self):
        try:
            print("Conectando a la base de datos...")  # Debug
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            cursor = db.cursor()
            query = """
            SELECT id_Aspirante, CONCAT(nombres, ' ', apellidoPaterno, ' ', apellidoMaterno) AS nombre_completo
            FROM Aspirante
            WHERE estado_solicitud = 'Finalizado';
            """
            cursor.execute(query)
            aspirantes = cursor.fetchall()
            db.close()

            print("Datos recuperados:", aspirantes)  # Debug

            for aspirante in aspirantes:
                # Añadir nombre completo
                name_btn = Button(
                    text=aspirante[1],
                    size_hint_y=None,
                    height=50,
                    background_color=(0.0, 0.4, 0.4, 1),
                    color=(1, 1, 1, 1)
                )
                self.ids.data_layout.add_widget(name_btn)

                # Añadir botón de acción
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
        print(f"Cargando pantalla de detalle para aspirante con ID: {aspirante_id}")
        detalle_screen = self.manager.get_screen("detalle_cct")
        detalle_screen.load_initial_ccts(aspirante_id)  # Cambia a 'load_initial_ccts'
        self.manager.current = "detalle_cct"

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

            # Obtener ubicación y nivel educativo del aspirante
            query_aspirante = """
            SELECT ResidenciaAspirante.estado, ResidenciaAspirante.municipio, InfoEducativaAspirante.nivelEducativo
            FROM ResidenciaAspirante
            JOIN InfoEducativaAspirante ON ResidenciaAspirante.id_Aspirante = InfoEducativaAspirante.id_Aspirante
            WHERE ResidenciaAspirante.id_Aspirante = %s;
            """
            cursor.execute(query_aspirante, (aspirante_id,))
            aspirante_data = cursor.fetchone()

            if not aspirante_data:
                print("No se encontraron datos del aspirante.")  # Debug
                return

            estado, municipio, nivel_educativo = aspirante_data
            print(f"Ubicación: {estado}, {municipio}, Nivel Educativo: {nivel_educativo}")  # Debug

            self.ids.aspirante_info.text = f"Estado: {estado}\nMunicipio: {municipio}"
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
                cct_info = (
                    f"[b]CCT:[/b] {cct[0]}\n"
                    f"[b]Nombre:[/b] {cct[1]}\n"
                    f"[b]Estado:[/b] {cct[2]}\n"
                    f"[b]Municipio:[/b] {cct[3]}\n"
                    f"[b]Nivel Educativo:[/b] {cct[4]}\n"
                    f"[b]Cupos Disponibles:[/b] {cct[5]}"
                )
                cct_label = Button(
                    text=cct_info,
                    size_hint_y=None,
                    height=150,
                    markup=True,
                    background_color=(0.0, 0.4, 0.4, 1),
                    color=(1, 1, 1, 1)
                )
                self.ids.cct_list.add_widget(cct_label)
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
                cct_info = f"{cct[1]} - {cct[3]} (Cupos: {cct[5]})"
                cct_btn = Button(
                    text=cct_info,
                    size_hint_y=None,
                    height=50,
                    background_color=(0.0, 0.4, 0.4, 1),
                    color=(1, 1, 1, 1)
                )
                cct_btn.bind(on_release=partial(self.assign_cct, self.aspirante_id, cct[0]))
                self.ids.cct_list.add_widget(cct_btn)

        except mysql.connector.Error as err:
            print(f"Error al buscar CCTs: {err}")

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

            # Actualizar base de datos
            query_assign = """
            INSERT INTO AsignacionAspiranteCCT (id_Aspirante, claveCentro, fecha_asignacion)
            VALUES (%s, %s, CURDATE());
            """
            cursor.execute(query_assign, (aspirante_id, clave_centro))

            query_update_cupos = """
            UPDATE CCT SET cupos_disponibles = cupos_disponibles - 1 WHERE claveCentro = %s;
            """
            cursor.execute(query_update_cupos, (clave_centro,))
            db.commit()
            db.close()

            print("CCT asignado correctamente.")  # Debug
            self.manager.current = "main"
        except mysql.connector.Error as err:
            print(f"Error al asignar CCT: {err}")

    def go_back(self):
        print("Regresando a la pantalla principal...")  # Debug
        self.manager.current = "main"

class AsignacionCCTApp(App):
    def build(self):
        print("Inicializando la aplicación...")  # Debug
        return Builder.load_file("asignacion_cct_practicas.kv")


if __name__ == "__main__":
    AsignacionCCTApp().run()