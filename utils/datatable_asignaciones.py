from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.properties import ObjectProperty

Builder.load_string('''
<DataTableAsignacion>:
    id: main_win
    RecycleView:
        viewclass: 'CustButton'
        id: table_floor
        RecycleGridLayout:
            id: table_floor_layout
            cols: 4  # Aumentamos las columnas para incluir botones
            default_size: (None, 250)
            default_size_hint: (1, None)
            size_hint_y: None
            height: self.minimum_height
            spacing: 5

<CustButton@Button>:
    size_hint_y: None
    height: 30
    bcolor: (0.5, 0.5, 0.5, 1)
    index: 0
    callback: None  # Nueva propiedad para almacenar la referencia de callback
    on_release: self.callback(self.text, self.index) if self.callback else None
    canvas.before:
        Color:
            rgba: root.bcolor
        Rectangle:
            size: self.size
            pos: self.pos
''')

class DataTableAsignacion(BoxLayout):
    def __init__(self, table='', callback=None, **kwargs):
        super().__init__(**kwargs)

        col_titles = [k for k in table.keys()]
        rows_len = len(table[col_titles[0]])
        self.columns = len(col_titles)  # Definimos el número de columnas basándonos en el número de títulos
        table_data = []

        # Encabezados de la tabla
        table_data.append({'text': 'Vista', 'size_hint_y': None, 'height': 50, 'bcolor': (.06, .45, .45, 1)})
        for t in col_titles[1:]:
            table_data.append({'text': str(t), 'size_hint_y': None, 'height': 50, 'bcolor': (.06, .45, .45, 1)})

        # Agregar filas de datos y botones asociados con el `user_id`
        for r in range(rows_len):
            # Extraemos `user_id` de la primera columna
            user_id = table[col_titles[0]][r]

            # Botón "Ver" asociado al `user_id`
            view_button = {
                'text': 'Ver',
                'size_hint_y': None,
                'height': 30,
                'bcolor': (.75, .12, .25, 1),
                'index': r,
                'callback': lambda btn_text, idx, user_id=user_id: callback(btn_text, user_id)  # Pasamos el `user_id` al callback
            }
            table_data.append(view_button)

            # Agregar datos de la fila
            for t in col_titles[1:]:
                table_data.append({
                    'text': str(table[t][r]),
                    'size_hint_y': None,
                    'height': 30,
                    'bcolor': (.06, .25, .25, 1)
                })

        # Configurar columnas y datos en el layout
        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data
