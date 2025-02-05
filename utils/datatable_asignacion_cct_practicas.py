from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from db_connection import execute_query

class DataTableAsignacionCCT(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        print("Inicializando DataTableAsignacionCCT...")  # Debug
        self.create_table()

    def create_table(self):
        print("Ejecutando create_table()...")  # Debug
        try:
            # Consulta para recuperar datos de aspirantes con estado_solicitud = 'Finalizado'
            query = """
            SELECT id_Aspirante, CONCAT(nombres, ' ', apellidoPaterno, ' ', apellidoMaterno) AS nombre_completo
            FROM Aspirante
            WHERE estado_solicitud = 'Finalizado';
            """
            print("Ejecutando consulta SQL...")  # Debug
            aspirantes = execute_query(query)

            print("Datos recuperados de la base de datos:", aspirantes)  # Debug

            # Crear tabla con los datos
            table = GridLayout(cols=2, size_hint_y=None, spacing=5)
            table.bind(minimum_height=table.setter('height'))

            if aspirantes:
                for aspirante in aspirantes:
                    print(f"Añadiendo aspirante: {aspirante['nombre_completo']}")  # Debug
                    # Columna: Nombre completo
                    table.add_widget(Button(
                        text=aspirante['nombre_completo'],
                        size_hint_y=None,
                        height=40,
                        halign='left',
                        valign='middle'
                    ))

                    # Columna: Botón para asignar CCT
                    asignar_btn = Button(
                        text="Asignar CCT",
                        size_hint_y=None,
                        height=40,
                        background_color=(0.7, 0, 0, 1),
                        color=(1, 1, 1, 1)
                    )
                    asignar_btn.bind(on_release=lambda btn, asp_id=aspirante['id_Aspirante']: self.asignar_cct(asp_id))
                    table.add_widget(asignar_btn)
            else:
                # Mensaje si no hay datos
                print("No hay aspirantes con estado 'Finalizado'.")  # Debug
                table.add_widget(Button(text="No hay datos disponibles", size_hint_y=None, height=40))

            scroll = ScrollView(size_hint=(1, 1))
            scroll.add_widget(table)
            self.add_widget(scroll)

        except Exception as err:
            print(f"Error al recuperar los datos: {err}")  # Debug

    def asignar_cct(self, aspirante_id):
        print(f"Aspirante seleccionado para asignar CCT: {aspirante_id}")  # Debug
        # Aquí puedes cambiar de pantalla o realizar la acción necesaria
