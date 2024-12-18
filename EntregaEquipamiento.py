from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Ellipse
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from math import sqrt
import mysql.connector
import json
import random
import random

class Node:
    def __init__(self, x, y, latitud=0, longitud=0, cct=None):
        self.x = x
        self.y = y
        self.latitud = latitud  # Coordenada geográfica
        self.longitud = longitud  # Coordenada geográfica
        self.cct = cct

    def distance_to(self, other):
        # Cálculo de distancia basado en latitud y longitud
        return sqrt((self.latitud - other.latitud)**2 + (self.longitud - other.longitud)**2)

class MapEditor(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nodes = []  # Lista de nodos
        self.node_graphics = []  # Referencias a los gráficos de los nodos (círculos)
        self.lines = []  # Lista de líneas (pares de nodos)
        self.selected_cct = None
        self.map_image = None  # Imagen del mapa cargado
        self.selected_state = None  # Estado seleccionado

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        # Agregar nodo al hacer clic en el mapa
        self.add_node(touch.pos)

    def add_node(self, pos):
        x, y = pos
        # Obtener latitud y longitud del CCT seleccionado (si existe)
        latitud, longitud = 0, 0
        if self.selected_cct:
            latitud, longitud = self.get_cct_coordinates(self.selected_cct)

        #print(latitud,' ', longitud)

        # Crear el nodo con ambas coordenadas
        node = Node(x=x, y=y, latitud=latitud, longitud=longitud, cct=self.selected_cct)
        """
        self.nodes.append(node)

        # Dibujar el nodo en la interfaz
        with self.canvas:
            Color(1, 0, 0)
            ellipse = Ellipse(pos=(x - 5, y - 5), size=(10, 10))
            self.node_graphics.append(ellipse)  # Guardar referencia del círculo
        """
        # Mostrar menú de opciones al hacer clic en el nodo
        self.node_options_menu(node)

    def get_cct_coordinates(self, cct_name):
        cct = cct_name.split()
        cct = cct[0]
        """
        Obtiene las coordenadas de latitud y longitud de un CCT desde la base de datos.
        Si no están disponibles, retorna (0, 0).
        """
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="conafe"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT latitud, longitud FROM CCT WHERE claveCentro = %s", (cct,))
        result = cursor.fetchone()
        conn.close()

        if result:
            latitud = result[0] if result[0] is not None else 0
            longitud = result[1] if result[1] is not None else 0
            print(f'Nodo: {latitud,longitud}')
            return latitud, longitud
        return 0, 0

    def connect_nodes(self):
        self.lines.clear()
        self.graph = {}  # Grafo como diccionario {nodo: {vecino: distancia}}
        with self.canvas:
            Color(0, 0, 1)  # Color azul para las conexiones normales
            for i, n1 in enumerate(self.nodes):
                self.graph[n1] = {}
                for j, n2 in enumerate(self.nodes):
                    if i != j:
                        distance = n1.distance_to(n2)  # Basado en latitud y longitud
                        Line(points=[n1.x, n1.y, n2.x, n2.y])  # Línea en la interfaz
                        self.graph[n1][n2] = distance
        
        # Calcular y dibujar la ruta más corta automáticamente
        path, length = self.find_shortest_path_aco()
        print(f"Ruta más corta encontrada: {path} con longitud {length}")
        self.draw_shortest_path(path)

    
    def find_shortest_path_aco(self, iterations=100, alpha=1.0, beta=2.0, evaporation_rate=0.5, pheromone_deposit=1.0):
        # Inicialización
        pheromones = {n1: {n2: 1.0 for n2 in neighbors} for n1, neighbors in self.graph.items()}
        best_path = None
        best_path_length = float('inf')
        epsilon = 1e-6  # Valor mínimo para evitar división entre 0

        for _ in range(iterations):
            paths = []
            path_lengths = []

            for _ in range(len(self.nodes)):  # Simulación de hormigas
                unvisited = set(self.nodes)
                current_node = random.choice(self.nodes)
                path = [current_node]
                path_length = 0

                while unvisited:
                    unvisited.discard(current_node)
                    probabilities = []

                    # Cálculo de probabilidades para elegir el siguiente nodo
                    for neighbor in self.graph[current_node]:
                        if neighbor in unvisited:
                            pheromone = pheromones[current_node][neighbor] ** alpha
                            visibility = (1.0 / max(self.graph[current_node][neighbor], epsilon)) ** beta
                            probabilities.append((neighbor, pheromone * visibility))

                    if probabilities:
                        total = sum(prob for _, prob in probabilities)
                        probabilities = [(node, prob / total) for node, prob in probabilities]
                        next_node = random.choices([p[0] for p in probabilities], weights=[p[1] for p in probabilities])[0]
                        path_length += self.graph[current_node][next_node]
                        path.append(next_node)
                        current_node = next_node
                    else:
                        break

                paths.append(path)
                path_lengths.append(path_length)

            # Actualización de feromonas
            for n1, neighbors in pheromones.items():
                for n2 in neighbors:
                    pheromones[n1][n2] *= (1 - evaporation_rate)  # Evaporación

            for path, length in zip(paths, path_lengths):
                if length < best_path_length:
                    best_path_length = length
                    best_path = path

                # Evitar división por 0 al actualizar feromonas
                if length > epsilon:  # Solo actualiza si length es mayor a epsilon
                    for i in range(len(path) - 1):
                        pheromones[path[i]][path[i + 1]] += pheromone_deposit / length

        return best_path, best_path_length


    def draw_shortest_path(self, path):
        """Dibuja la ruta más corta calculada y muestra una alerta con la ruta en forma de lista."""
        if not path:
            return

        # Dibuja la ruta en el canvas
        with self.canvas:
            Color(0, 1, 0)  # Verde para ruta más corta
            for i in range(len(path) - 1):
                Line(points=[path[i].x, path[i].y, path[i + 1].x, path[i + 1].y])

        # Crear el mensaje de la ruta en términos de CCT (en forma de lista)
        cct_route = [f"{i + 1}. {node.cct}" for i, node in enumerate(path)]
        route_message = "\n".join(cct_route)

        # Mostrar la ruta en un Popup
        popup_content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_content.add_widget(Label(text=f"Ruta más corta:\n{route_message}", halign='left', valign='middle', font_size=14))
        close_button = Button(text="Cerrar", size_hint=(1, 0.3))
        popup = Popup(title="Ruta Más Corta", content=popup_content, size_hint=(0.8, 0.6))
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def save_to_json(self, filename):
        """
        Guarda los nodos y la imagen del mapa en un archivo JSON.
        """
        try:
            data = {
                "nodes": [
                    {
                        "x": node.x,
                        "y": node.y,
                        "latitud": float(node.latitud),
                        "longitud": float(node.longitud),
                        "cct": node.cct
                    }
                    for node in self.nodes
                ],
                "map_image": self.map_image.source if self.map_image else None
            }

            with open(filename, "w") as file:
                json.dump(data, file, indent=4)  # Intentar guardar en JSON
            print(f"Datos guardados correctamente en {filename}")
        except TypeError as e:
            print(f"Error al guardar en JSON: {e}")
            print(f"Datos problemáticos: {data}")
    
    def load_from_json(self, filename):
        """
        Carga los nodos y la imagen del mapa desde un archivo JSON.
        """
        with open(filename, "r") as file:
            data = json.load(file)

        # Limpiar nodos y canvas actuales
        self.clear()

        # Cargar la imagen del mapa
        if "map_image" in data and data["map_image"]:
            self.set_image(data["map_image"])

        # Cargar nodos
        for node_data in data.get("nodes", []):
            node = Node(
                x=node_data["x"],
                y=node_data["y"],
                latitud=node_data["latitud"],
                longitud=node_data["longitud"],
                cct=node_data["cct"]
            )
            self.nodes.append(node)

            # Dibujar el nodo en el canvas
            with self.canvas:
                Color(1, 0, 0)
                Ellipse(pos=(node.x - 5, node.y - 5), size=(10, 10))

        print(f"Datos cargados correctamente desde {filename}")

    def save_state(self, file_path):
        data = {
            'nodes': [{'x': node.x, 'y': node.y, 'cct': node.cct} for node in self.nodes],
            'map_image': self.map_image.source if self.map_image else None
        }
        with open(file_path, 'w') as f:
            json.dump(data, f)

    # Modificar load_state para cargar un archivo específico
    def load_state(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"Datos cargados desde {file_path}: {data}")  # Depuración
                self.clear()
                if data.get('map_image'):
                    self.set_image(data['map_image'])
                for node_data in data['nodes']:
                    node = Node(node_data['x'], node_data['y'], node_data['cct'])
                    self.nodes.append(node)
                    with self.canvas:
                        Color(1, 0, 0)
                        Ellipse(pos=(node.x - 5, node.y - 5), size=(10, 10))
        except FileNotFoundError:
            print(f"Archivo no encontrado: {file_path}")  # Depuración


    def clear(self):
        self.nodes.clear()
        self.lines.clear()
        self.canvas.clear()

    def node_options_menu(self, node):
        menu = ModalView(size_hint=(0.5, 0.3))
        layout = BoxLayout(orientation='vertical')

        btn_assign_cct = Button(text="Asignar CCT")
        btn_assign_cct.bind(on_release=lambda _: self.show_cct_dropdown(node, btn_assign_cct))

        btn_delete_node = Button(text="Eliminar Nodo")
        btn_delete_node.bind(on_release=lambda _: self.delete_node(node, menu))

        layout.add_widget(btn_assign_cct)
        layout.add_widget(btn_delete_node)
        menu.add_widget(layout)
        menu.open()

    def show_cct_dropdown(self, node, btn_assign_cct):
        if not hasattr(self, 'cct_dropdown'):
            self.cct_dropdown = DropDown()

        self.cct_dropdown.clear_widgets()
        for cct in self.available_ccts:
            btn = Button(text=cct, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.assign_cct_to_node(node, btn.text))
            self.cct_dropdown.add_widget(btn)

        self.cct_dropdown.open(btn_assign_cct)

    def assign_cct_to_node(self, node, cct_name):
        node.cct = cct_name
        self.available_ccts.remove(cct_name)

        # Obtener latitud y longitud desde la base de datos
        latitud, longitud = self.get_cct_coordinates(cct_name)
        node.latitud = latitud
        node.longitud = longitud

        # Agregar el nodo a la lista y dibujarlo
        self.nodes.append(node)
        with self.canvas:
            Color(1, 0, 0)
            ellipse = Ellipse(pos=(node.x - 5, node.y - 5), size=(10, 10))
            self.node_graphics.append(ellipse)

        self.cct_dropdown.dismiss()
        #menu.dismiss()

    def delete_node(self, node, menu):
        # Eliminar nodo de la lista
        if node.cct:
            self.available_ccts.append(node.cct)
        if node in self.nodes:
            index = self.nodes.index(node)
            self.nodes.remove(node)
            
            # Eliminar el último círculo asociado al nodo
            if index < len(self.node_graphics):
                self.canvas.remove(self.node_graphics[index])
                del self.node_graphics[index]
        
        menu.dismiss()

    def set_image(self, image_path):
        self.map_image = Image(
            source=image_path,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        self.clear_widgets()
        self.add_widget(self.map_image)

class EquipamientoScreen(BoxLayout):
    
    def find_and_draw_shortest_path(self, instance):
        """Calcula y dibuja la ruta más corta."""
        path, length = self.map_editor.find_shortest_path_aco()
        print(f"Ruta más corta encontrada: {path} con longitud {length}")
        self.map_editor.draw_shortest_path(path)
        
    def build(self):
        layout = BoxLayout(orientation='vertical')

        header = BoxLayout(size_hint_y=0.1)
        
        btn_load_image = Button(text="Cargar Imagen")
        btn_load_image.bind(on_release=self.load_image)

        btn_save = Button(text="Guardar")
        btn_save.bind(on_release=lambda _: self.save_state_for_selected_state())

        btn_connect = Button(text="Conectar Nodos")
        btn_connect.bind(on_release=lambda _: self.map_editor.connect_nodes())

        btn_clear = Button(text="Limpiar Mapa")
        btn_clear.bind(on_release=lambda _: self.map_editor.clear())

        header.add_widget(btn_load_image)
        header.add_widget(btn_save)
        header.add_widget(btn_connect)
        header.add_widget(btn_clear)

        self.map_editor = MapEditor()

        footer = BoxLayout(size_hint_y=0.1)

        state_dropdown = DropDown()
        self.load_states(state_dropdown)

        state_button = Button(text="Seleccionar Estado")
        state_button.bind(on_release=state_dropdown.open)
        state_dropdown.bind(on_select=lambda instance, x: self.update_state_selection(state_button, x))
        footer.add_widget(state_button)

        # Botón de regresar
        btn_back = Button(text="Regresar")
        btn_back.bind(on_release=self.go_back)
        footer.add_widget(btn_back)


        layout.add_widget(header)
        layout.add_widget(self.map_editor)
        layout.add_widget(footer)

        return layout

    def go_back(self, instance):
        # Implementa aquí la funcionalidad deseada, como cerrar la pantalla o navegar al menú principal
        print("Regresando al menú principal...")

    def update_state_selection(self, button, state_name):
        button.text = state_name
        self.map_editor.available_ccts = self.get_ccts_by_state(state_name)
        self.map_editor.selected_state = state_name  # Guardar el estado seleccionado

        # Construir la ruta del archivo JSON basado en el estado seleccionado
        file_path = f"{state_name}_map_state.json"
        print(f"Intentando cargar el archivo JSON: {file_path}")  # Depuración

        try:
            # Intentar cargar el archivo JSON
            self.map_editor.load_from_json(file_path)
            print(f"Archivo {file_path} cargado exitosamente.")
        except FileNotFoundError:
            # Si el archivo no existe, limpiar el mapa y mostrar un mensaje
            self.map_editor.clear()
            print(f"No se encontró un archivo JSON para el estado: {state_name}")

    def save_state_for_selected_state(self):
        # Guardar el estado actual en un archivo JSON con el nombre del estado seleccionado
        if self.map_editor.selected_state:
            file_path = f"{self.map_editor.selected_state}_map_state.json"
            self.map_editor.save_to_json(file_path)
            #self.map_editor.save_state(file_path)
        else:
            print("Seleccione un estado antes de guardar.")

    def load_image(self, instance):
        filechooser = FileChooserIconView()
        popup = Popup(title="Seleccionar Mapa", content=filechooser, size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=lambda fc, selection, touch: self.set_image(selection, popup))
        popup.open()

    def load_json(self, instance):
        filechooser = FileChooserIconView()
        popup = Popup(title="Seleccionar JSON", content=filechooser, size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=lambda fc, selection, touch: self.set_json(selection, popup))
        popup.open()

    def set_image(self, selection, popup):
        if selection:
            self.map_editor.set_image(selection[0])
        popup.dismiss()

    def set_json(self, selection, popup):
        if selection:
            self.map_editor.load_from_json(selection[0])
        popup.dismiss()

    def load_states(self, dropdown):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="conafe"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT estado FROM CCT")
        states = cursor.fetchall()

        for state in states:
            state_name = state[0]
            btn = Button(text=state_name, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        conn.close()

    def get_ccts_by_state(self, state):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="conafe"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT claveCentro, nombre FROM CCT WHERE estado = %s", (state,))
        ccts = cursor.fetchall()
        conn.close()
        return [f"{clave} ({nombre})" for clave, nombre in ccts]

class MainApp(App):
    def build(self):
        return EquipamientoScreen()

if __name__ == '__main__':
    MainApp().run()