from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.properties import ObjectProperty

Builder.load_string('''
<DataTableAlumnos>:
    id: main_win
    RecycleView:
        viewclass: 'CustButton'
        id: table_floor
        RecycleGridLayout:
            id: table_floor_layout
            cols: 4  # Ajustado para 4 columnas: CURP, nombres, apellido_paterno, nivel
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
    callback: None
    on_release: self.callback(self.text, self.index) if self.callback else None
    canvas.before:
        Color:
            rgba: root.bcolor
        Rectangle:
            size: self.size
            pos: self.pos
''')

class DataTableAlumnos(BoxLayout):
    def __init__(self, table='', callback=None, **kwargs):
        super().__init__(**kwargs)

        # Filtrar las columnas relevantes
        col_titles = [k for k in table.keys()]
        rows_len = len(table[col_titles[0]])
        self.columns = len(col_titles)
        table_data = []

        # Encabezados de la tabla
        for t in col_titles:
            table_data.append({
                'text': str(t),
                'size_hint_x': 0.25,  # Ancho uniforme para todas las columnas
                'size_hint_y': None,
                'height': 50,
                'bcolor': (.06, .45, .45, 1)
            })

        # Filas de datos
        for r in range(rows_len):
            for t in col_titles:
                table_data.append({
                    'text': str(table[t][r]),
                    'size_hint_x': 0.25,
                    'size_hint_y': None,
                    'height': 30,
                    'bcolor': (.06, .25, .25, 1)
                })

        # Configurar columnas y datos en el layout
        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data
