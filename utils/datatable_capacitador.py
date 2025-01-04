from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from db_connection import execute_query

class DataTableCapacitadorAspirante(BoxLayout):
    def __init__(self, table = '', db_config=None, id_capacitador=None,**kwargs):
        super().__init__(orientation='vertical',**kwargs)
        # Configuración de conexión a la base de datos  
        if not isinstance(db_config, dict):
            raise ValueError("db_config debe ser un diccionario con la configuración de la base de datos.")

        self.id_capacitador = id_capacitador
        self.db_config = db_config

        # Contenedor principal con fondo blanco
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Fondo blanco
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # ScrollView para la tabla principal
        self.main_layout = BoxLayout(orientation='vertical')
        self.tabla_scroll = ScrollView(size_hint=(1, 1))  # Asegurar que ocupe todo el espacio
        self.tabla = GridLayout(cols=4, size_hint_y=None)
        self.tabla.bind(minimum_height=self.tabla.setter('height'))

        # Encabezados de la tabla principal
        encabezados = ['Info', 'Nombre', 'Estado Capacitación', 'Cambiar Estado']
        for encabezado in encabezados:
            self.tabla.add_widget(Label(text=encabezado, size_hint_y=None, height=40, bold=True, color=(.06, .45, .45, 1)))

        # Filas de datos con información adicional del aspirante
        self.datos = [
            ("Info 1", "Nombre 1", "Pendiente", "Detalles sobre la capacitación 1", "Edad: 25\nTeléfono: 123-456-7890"),
            ("Info 2", "Nombre 2", "Completo", "Detalles sobre la capacitación 2", "Edad: 30\nTeléfono: 987-654-3210"),
            ("Info 3", "Nombre 3", "En curso", "Detalles sobre la capacitación 3", "Edad: 28\nTeléfono: 456-789-0123"),
        ]

        col_titles = [k for k in table.keys()]
        rows_len = len(table[col_titles[0]]) 

        for r in range(rows_len):
            id_aspirante = table['id_Aspirante'][r]
            nombre = table['nombres'][r]
            observaciones = table['observaciones'][r]
            estadoCapacitacion = table['estadoCapacitacion'][r]
            aPaterno = table['apellidoPaterno'][r]
            aMaterno = table['apellidoMaterno'][r]
            fechaInicio = table['fechaInicio'][r]
            fechaFin = table['fechaFinalizacion'][r]
            # Columna Info como botón
            boton_info = Button(
                text= "Ver",
                size_hint_y=None,
                height=40,
                background_color=(0.5, 0.5, 0.5, 1),  # Botón gris
                color=(1, 1, 1, 1),  # Texto blanco
            )
            boton_info.bind(on_press=lambda instance, id_aspirante=id_aspirante,observaciones=observaciones, aPaterno=aPaterno, aMaterno=aMaterno, fechaInicio=fechaInicio, fechaFin=fechaFin: self.mostrar_detalle(id_aspirante, observaciones, aPaterno, aMaterno, fechaInicio, fechaFin))
            self.tabla.add_widget(boton_info)

            # Columna Nombre
            self.tabla.add_widget(Label(text=nombre, size_hint_y=None, height=40, color=(0, 0, 0, 1)))  # Texto negro

            # Columna Estado Capacitación
            estado_label = Label(text=estadoCapacitacion, size_hint_y=None, height=40, color=(0, 0, 0, 1))  # Texto negro
            self.tabla.add_widget(estado_label)

            # Columna Cambiar Estado con funcionalidad
            boton_cambiar = Button(
                text="Cambiar",
                size_hint_y=None,
                height=40,
                background_color=(0.5, 0.5, 0.5, 1),  # Botón gris
                color=(1, 1, 1, 1),  # Texto blanco
            )
            boton_cambiar.bind(on_press=lambda instance, estado_label=estado_label, id_aspirante=id_aspirante: self.mostrar_opciones_estado(estado_label, id_aspirante))
            self.tabla.add_widget(boton_cambiar)

        # Agregar la tabla al ScrollView
        self.tabla_scroll.add_widget(self.tabla)
        self.main_layout.add_widget(self.tabla_scroll)

        # Agregar el layout principal al contenedor principal
        self.add_widget(self.main_layout)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def mostrar_tabla(self, *args):
        # Limpia el layout principal y agrega de nuevo la tabla
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.tabla_scroll)

    def mostrar_detalle(self, id_aspirante, observaciones, aPaterno, aMaterno, fechaInicio, fechaFin):
        # Crear un layout principal para el detalle
        detalle_main_layout = BoxLayout(orientation='vertical', size_hint=(1, 1))

        # Crear dinámicamente un ScrollView
        detalle_scroll = ScrollView(size_hint=(1, 0.9))  # Parte superior para el contenido
        detalle_layout = GridLayout(cols=2, size_hint_y=None, padding=10, spacing=10)
        detalle_layout.bind(minimum_height=detalle_layout.setter('height'))

        # Encabezados para los detalles
        detalle_layout.add_widget(Label(text="Campo", size_hint_y=None, height=40, bold=True, color=(0, 0, 0, 1)))
        detalle_layout.add_widget(Label(text="Valor", size_hint_y=None, height=40, bold=True, color=(0, 0, 0, 1)))

        # Información del aspirante
        detalle_layout.add_widget(Label(text="Apellido Paterno", size_hint_y=None, height=40, color=(0, 0, 0, 1)))
        detalle_layout.add_widget(Label(text=str(aPaterno) if aPaterno is not None else "No disponible", size_hint_y=None, height=40, color=(0, 0, 0, 1)))

        detalle_layout.add_widget(Label(text="Apellido Materno", size_hint_y=None, height=40, color=(0, 0, 0, 1)))
        detalle_layout.add_widget(Label(text=str(aMaterno) if aMaterno is not None else "No disponible", size_hint_y=None, height=40, color=(0, 0, 0, 1)))

        detalle_layout.add_widget(Label(text="Fecha Inicio capacitación", size_hint_y=None, height=40, color=(0, 0, 0, 1)))
        detalle_layout.add_widget(Label(text=str(fechaInicio) if fechaInicio is not None else "No disponible", size_hint_y=None, height=40, color=(0, 0, 0, 1)))

        detalle_layout.add_widget(Label(text="Fecha fin de capacitación", size_hint_y=None, height=40, color=(0, 0, 0, 1)))
        detalle_layout.add_widget(Label(text=str(fechaFin) if fechaFin is not None else "No disponible", size_hint_y=None, height=40, color=(0, 0, 0, 1)))

        # Detalles de la capacitación
        detalle_layout.add_widget(Label(text="Observaciones de la Capacitación", size_hint_y=None, height=40, color=(0, 0, 0, 1)))
        detalle_layout.add_widget(Label(text=str(observaciones) if observaciones is not None else "No disponible", size_hint_y=None, height=40, color=(0, 0, 0, 1)))

        # Agregar el layout al ScrollView
        detalle_scroll.add_widget(detalle_layout)

        # Botón para regresar en la parte inferior
        boton_regresar = Button(
            text="Regresar a la Tabla",
            size_hint=(1, 0.1),
            height=50,
            background_color=(0.5, 0.5, 0.5, 1),  # Botón gris
            color=(1, 1, 1, 1),  # Texto blanco
        )
        boton_regresar.bind(on_press=self.mostrar_tabla)

        # Agregar ScrollView y botón al layout principal de detalle
        detalle_main_layout.add_widget(detalle_scroll)
        detalle_main_layout.add_widget(boton_regresar)

        # Limpiar el layout principal y mostrar el nuevo layout de detalle
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(detalle_main_layout)

    def mostrar_opciones_estado(self, estado_label, id_aspirante):
        # Crear un layout principal para las opciones de estado
        opciones_main_layout = BoxLayout(orientation='vertical', size_hint=(1, 1))

        # Crear dinámicamente un ScrollView
        opciones_scroll = ScrollView(size_hint=(1, 0.7))  # Parte superior para las opciones
        opciones_layout = GridLayout(cols=1, size_hint_y=None, padding=10, spacing=10)
        opciones_layout.bind(minimum_height=opciones_layout.setter('height'))

        # Lista de estados disponibles
        estados_disponibles = ["En inicio", "Cursos intermedios", "Finalizando Cursos", "Finalizado", "Congelado", "Rechazado"]

        for estado in estados_disponibles:
            boton_estado = Button(
                text=estado,
                size_hint_y=None,
                height=40,
                background_color=(0.5, 0.5, 0.5, 1),  # Botón gris
                color=(1, 1, 1, 1),  # Texto blanco
            )

            # Al presionar un estado, se actualiza el estado_label y se guarda la observación
            # Asignar id_aspirante al botón
            boton_estado.bind(on_press=lambda instance, id_aspirante = id_aspirante, estado=estado: self.seleccionar_estado(instance, estado, estado_label, id_aspirante))
            opciones_layout.add_widget(boton_estado)

        # Agregar el layout al ScrollView
        opciones_scroll.add_widget(opciones_layout)

        # Campo para observaciones
        observaciones_input = TextInput(
            hint_text="Escriba observaciones aquí...",
            size_hint=(1, 0.2),
            multiline=True,
            background_color=(0.9, 0.9, 0.9, 1),  # Fondo gris claro
            foreground_color=(0, 0, 0, 1),  # Texto negro
        )

        # Botón para regresar
        boton_regresar = Button(
            text="Cancelar",
            size_hint=(1, 0.1),
            height=50,
            background_color=(0.5, 0.5, 0.5, 1),  # Botón gris
            color=(1, 1, 1, 1),  # Texto blanco
        )
        boton_regresar.bind(on_press=self.mostrar_tabla)

        # Agregar ScrollView, TextInput y botón al layout principal
        opciones_main_layout.add_widget(opciones_scroll)
        opciones_main_layout.add_widget(observaciones_input)
        opciones_main_layout.add_widget(boton_regresar)

        # Limpiar el layout principal y mostrar el nuevo layout de opciones
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(opciones_main_layout)

        # Al seleccionar un estado, también se guardará la observación
        self.observaciones_input = observaciones_input

    def seleccionar_estado(self, instance, estado, estado_label, id_aspirante):
        # Obtener la observación del usuario
        observacion = self.observaciones_input.text.strip()  # Quitar espacios innecesarios
        print(f"Estado seleccionado: {estado}")
        print(f"Observación: {observacion}")

        # Actualizar el estado del label correspondiente
        estado_label.text = estado

        # Actualizar en la base de datos
        self.actualizar_base_datos(id_aspirante, estado, observacion)

        # Regresar a la tabla principal
        self.go_back(instance)
    
    def actualizar_base_datos(self, id_aspirante, nuevo_estado, observacion):
        try:
            # Consulta SQL para actualizar los datos
            query = """
            UPDATE FII
            SET estadoCapacitacion = %s, observaciones = %s
            WHERE id_Aspirante = %s
            """
            # Ejecuta la consulta
            execute_query(query, (nuevo_estado, observacion, id_aspirante))
            print(f"Se actualizó el aspirante {id_aspirante} con estado '{nuevo_estado}' y observación '{observacion}'.")
        except Exception as err:
            print(f"Error al actualizar la base de datos: {err}")

    def go_back(self, instance):
        App.get_running_app().root.current = 'capacitador'