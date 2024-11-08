from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.properties import ObjectProperty

Builder.load_string('''
<DataTableConvUser>:
    id: main_win
    RecycleView:
        viewclass: 'CustButton'
        id: table_floor
        RecycleGridLayout:
            id: table_floor_layout
            cols: 5  # Número de columnas actualizado para incluir "Aspirantes"
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

class DataTableConvUser(BoxLayout):
    def __init__(self, table='', callback=None, **kwargs):  # Añadido parámetro callback
        super().__init__(**kwargs)

        col_titles = [k for k in table.keys()]
        rows_len = len(table[col_titles[0]])
        self.columns = len(col_titles) + 1  # Agregamos dos columnas para los botones de acción y aspirantes
        table_data = []

        # Encabezados de la tabla
        for t in col_titles[1:]:
            # Asignar ancho específico para cada columna
            if t == 'nombre':
                table_data.append({'text': str(t), 'size_hint_x': 0.5, 'size_hint_y': None, 'height': 50, 'bcolor': (.06, .45, .45, 1)})
            elif t in ['status']:
                table_data.append({'text': str(t), 'size_hint_x': 0.2, 'size_hint_y': None, 'height': 50, 'bcolor': (.06, .45, .45, 1)})
            else:
                table_data.append({'text': str(t), 'size_hint_x': 0.3, 'size_hint_y': None, 'height': 50, 'bcolor': (.06, .45, .45, 1)})
                
        table_data.append({'text': 'Documento', 'size_hint_x': 0.2, 'size_hint_y': None, 'height': 50, 'bcolor': (.06, .45, .45, 1)})
        table_data.append({'text': 'Formulario', 'size_hint_x': 0.2, 'size_hint_y': None, 'height': 50, 'bcolor': (.06, .45, .45, 1)})

        # Agregar filas de datos y botones, comenzando desde el segundo elemento (índice 1)
        for r in range(rows_len):
            for t in col_titles[1:]:  # Empezamos desde el segundo elemento, omitiendo el primero
                if t == 'nombre':
                    table_data.append({'text': str(table[t][r]), 'size_hint_x': 0.5, 'size_hint_y': None, 'height': 30, 'bcolor': (.06, .25, .25, 1)})
                elif t == 'status':
                    table_data.append({'text': str(table[t][r]), 'size_hint_x': 0.2, 'size_hint_y': None, 'height': 30, 'bcolor': (.06, .25, .25, 1)})
                else:
                    table_data.append({'text': str(table[t][r]), 'size_hint_x': 0.3, 'size_hint_y': None, 'height': 30, 'bcolor': (.06, .25, .25, 1)})



            # Botón de "Aspirantes"
            documento_button = {'text': 'Ver', 'size_hint_x': 0.2, 'size_hint_y': None, 'height': 30, 'bcolor': (.25, .55, .25, 1), 'index': r, 'callback': callback}
            table_data.append(documento_button)
            aspirantes_button = {'text': 'Aplicar', 'size_hint_x': 0.2, 'size_hint_y': None, 'height': 30, 'bcolor': (.25, .55, .25, 1), 'index': r, 'callback': callback}
            table_data.append(aspirantes_button)

        # Configurar columnas y datos en el layout
        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data
