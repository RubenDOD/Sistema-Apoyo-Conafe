from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty

Builder.load_string('''
<DataTableAlumnosAsign>:
    id: main_win
    RecycleView:
        viewclass: 'CustButton'
        id: table_floor
        RecycleGridLayout:
            id: table_floor_layout
            cols: 5  # Ajustado para 4 columnas: CURP, nombres, apellido_paterno, nivel
            default_size: (None, 250)
            default_size_hint: (1, None)
            size_hint_y: None
            height: self.minimum_height
            spacing: 5

<CustButton@Button>:
    size_hint_y: None
    height: 30
    bcolor: (0.5, 0.5, 0.5, 1)
    curp: ''  # Nueva propiedad para almacenar el CURP
    callback: None
    on_release: self.callback(self.curp) if self.callback else None
    canvas.before:
        Color:
            rgba: root.bcolor
        Rectangle:
            size: self.size
            pos: self.pos
''')

class DataTableAlumnosAsign(BoxLayout):
    def __init__(self, table='', callback=None, **kwargs):
        super().__init__(**kwargs)

        # Filtrar las columnas relevantes
        col_titles = [k for k in table.keys()]
        col_titles.append('Ver')  # Agregar columna "Ver"
        rows_len = len(table[list(table.keys())[0]])
        self.columns = len(col_titles)
        table_data = []

        # Encabezados de la tabla
        for t in col_titles:
            table_data.append({
                'text': str(t),
                'size_hint_x': 0.2,  # Ajustar tamaño para 5 columnas
                'size_hint_y': None,
                'height': 50,
                'bcolor': (.06, .45, .45, 1)
            })

        # Filas de datos
        for r in range(rows_len):
            for t in table.keys():
                table_data.append({
                    'text': str(table[t][r]),  # Solo text debe ser cadena
                    'size_hint_x': 0.2,  # Numérico correcto
                    'size_hint_y': None,
                    'height': 30,  # Numérico correcto
                    'bcolor': (.06, .25, .25, 1)  # Color en formato de tupla
                })
            # Agregar botón "Ver" a cada fila
            table_data.append({
            'text': 'Ver',
            'size_hint_x': 0.2,  # Esto sigue siendo numérico
            'size_hint_y': None,
            'height': 30,  # Esto sigue siendo numérico
            'bcolor': (.06, .45, .45, 1),
            'callback': callback,  # Pasar el callback
            'curp': table['CURP'][r]  # El CURP se pasa al callback aquí
        })
        # Configurar columnas y datos en el layout
        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data