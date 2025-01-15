from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import requests
from polyline import decode
from simplification.cutil import simplify_coords
from kivy.uix.scrollview import ScrollView
from db_connection import execute_query
import random
from kivy.lang import Builder

#Builder.load_file("EE.kv")

class GeneticAlgorithm:
    def __init__(self, distance_matrix, demands, start_index, population_size=50, generations=100, mutation_rate=0.05):
        self.distance_matrix = distance_matrix
        self.demands = [0] + demands
        self.start_index = start_index  # Índice del punto de inicio en la matriz
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.population = self.initialize_population()

    def initialize_population(self):
        population = []
        idx = list(range(len(self.distance_matrix)))
        idx.remove(self.start_index)  # Eliminar el punto de inicio de la lista de índices
        for _ in range(self.population_size):
            random.shuffle(idx)
            population.append([self.start_index] + idx)  # Añadir el punto de inicio al comienzo de cada ruta
        return population

    def calculate_fitness(self, individual):
        total_distance = 0
        for i in range(len(individual) - 1):
            start, end = individual[i], individual[i + 1]
            total_distance += self.distance_matrix[start][end]
        total_distance += self.demands[individual[0]]  # Solo sumar la demanda del punto de inicio
        return total_distance

    def selection(self):
        self.population.sort(key=self.calculate_fitness)
        self.population = self.population[:len(self.population) // 2]

    def crossover(self, parent1, parent2):
        cut = random.randint(1, len(parent1) - 1)
        child = parent1[:cut] + [x for x in parent2 if x not in parent1[:cut]]
        return child

    def mutate(self, individual):
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                j = random.randint(0, len(individual) - 1)
                individual[i], individual[j] = individual[j], individual[i]
        return individual

    def run(self):
        for _ in range(self.generations):
            self.selection()
            new_population = []
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(self.population, 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population
        best_solution = min(self.population, key=self.calculate_fitness)
        return best_solution

class EquipamientoScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(EquipamientoScreen, self).__init__(**kwargs)
        self.available_localidades = []  # Inicializar el atributo aquí

    def reset_screen(self):
        self.ids.algun_id.text = ""  # Reset text
        self.ids.otro_id.value = 0   # Reset values
        self.load_states()  # Assuming this method reloads the necessary data

    def go_back(self, instance):
        self.reset_screen()
        print("Returning to the main menu...")

    def update_state_selection(self, button, state_name):
        print("Displaying states")
        button.text = state_name
        localidades = self.get_localidades_by_state(state_name)
        if not localidades:
            print("No localidades found for state:", state_name)
            return
        self.available_localidades = localidades  # Almacenar las localidades obtenidas
        lat_lngs = ["{},{}".format(loc[2], loc[3]) for loc in self.available_localidades]
        demands = [loc[4] for loc in self.available_localidades]

        start_point = "19.847811,-90.535945"
        api_key = "AIzaSyAZC4UtWCoYayInA-CyzJ4lKso8PcJLtok"

        # Call the static method with all required arguments
        distance_matrix = self.create_distance_matrix(lat_lngs, start_point, api_key)

        print("Number of demands:", len(demands))
        print("Size of distance matrix:", len(distance_matrix))

        print(distance_matrix)

        ga = GeneticAlgorithm(distance_matrix, demands, start_index=0, population_size=50, generations=100, mutation_rate=0.01)
        optimized_route = ga.run()

        map_url = self.display_route_on_map(optimized_route, api_key)
        if map_url:
            print("Map URL:", map_url)
        else:
            print("Failed to generate map URL.")
            
    def get_localidades_by_state(self, state):
        try:
            sql = "SELECT municipio, localidad, latitud, longitud, UnidadesTotalEntrega FROM LocalidadesCampeche"
            localidades = execute_query(sql)
            return [[municipio, localidad, float(latitud), float(longitud), int(UnidadesTotalEntrega)] for municipio, localidad, latitud, longitud, UnidadesTotalEntrega in localidades]
        except Exception as e:
            print(f"Error getting localities: {e}")
            return []

    def create_distance_matrix(self, all_points, start_point, api_key):
        all_points = [start_point] + [pt for pt in all_points if pt != start_point]  # Asegúrate de que el punto de inicio es el primero
        n = len(all_points)
        matrix = [[float('inf')] * n for _ in range(n)]  # Usar 'inf' para inicializar la matriz

        max_points = 7  # Este número debe calcularse para que no exceda el límite de elementos permitidos
        for i in range(0, n, max_points):
            for j in range(0, n, max_points):
                sub_origins = all_points[i:i + max_points]
                sub_destinations = all_points[j:j + max_points]
                origins = "|".join(sub_origins)
                destinations = "|".join(sub_destinations)
                url = "https://maps.googleapis.com/maps/api/distancematrix/json"
                params = {
                    'origins': origins,
                    'destinations': destinations,
                    'key': api_key,
                    'mode': 'driving',
                }
                response = requests.get(url, params=params)
                data = response.json()
                if data['status'] == 'OK':
                    for x, row in enumerate(data['rows']):
                        for y, element in enumerate(row['elements']):
                            if element['status'] == 'OK':
                                matrix[i + x][j + y] = element['distance']['value']
                            else:
                                matrix[i + x][j + y] = float('inf')  # Tratar errores o lugares inaccesibles
                else:
                    print("Error:", data['status'])

        return matrix

    def get_distance_matrix(self, lat_lngs, demands, api_key="AIzaSyAZC4UtWCoYayInA-CyzJ4lKso8PcJLtok"):
        origins = "|".join(["{},{}".format(lat, lng) for lat, lng in lat_lngs])
        destinations = origins
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': origins,
            'destinations': destinations,
            'key': api_key,
            'mode': 'driving',
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            matrix = []
            for row in data['rows']:
                row_distances = [element['distance']['value'] for element in row['elements']]
                matrix.append(row_distances)
            return matrix
        else:
            print("Error obtaining distance matrix:", data['status'])
            return None

    def display_route_on_map(self, optimized_route, api_key):
        # Convertir índices a coordenadas
        waypoints = [
            "{},{}".format(self.available_localidades[idx-1][2], self.available_localidades[idx-1][3])
            if idx != 0 else "19.847811,-90.535945"
            for idx in optimized_route
        ]

        # Crear marcadores para las localidades optimizadas
        markers = [
            f"color:red|label:{i+1}|{self.available_localidades[idx-1][2]},{self.available_localidades[idx-1][3]}"
            if idx != 0 else f"color:green|label:Inicio|19.847811,-90.535945"
            for i, idx in enumerate(optimized_route)
        ]

        # Concatenar todos los marcadores
        markers_param = "&markers=".join(markers)

        # Calcular el centro geográfico
        latitudes = [float(wp.split(",")[0]) for wp in waypoints]
        longitudes = [float(wp.split(",")[1]) for wp in waypoints]
        center_lat = sum(latitudes) / len(latitudes)
        center_lng = sum(longitudes) / len(longitudes)

        # Ajustar zoom más refinado
        lat_range = max(latitudes) - min(latitudes)
        lng_range = max(longitudes) - min(longitudes)
        max_range = max(lat_range, lng_range)

        if max_range < 0.05:
            zoom = 14
        elif max_range < 0.1:
            zoom = 12
        elif max_range < 0.5:
            zoom = 10
        elif max_range < 1:
            zoom = 8
        else:
            zoom = 6

        # Generar la URL para el mapa
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?size=800x600&center={center_lat},{center_lng}&zoom={zoom}&{markers_param}&key={api_key}"

        # Descargar la imagen del mapa
        image_path = "map_image.png"
        response = requests.get(map_url, stream=True)
        if response.status_code == 200:
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            # Actualizar la imagen en la interfaz de Kivy
            self.ids.map_image.source = image_path
            self.ids.map_image.reload()
            print(f"Map image saved to {image_path} and displayed.")
        else:
            print(f"Failed to download map image. Status code: {response.status_code}")

        # Mostrar detalles de los viajes en un Popup
        self.display_travel_directions(optimized_route, api_key)

    def display_travel_directions(self, optimized_route, api_key):
        """
        Mostrar un popup con la información de la ruta optimizada.
        """
        # Punto inicial fijo
        start_point_name = "Palacio Federal, Zona Centro San Francisco"
        start_point_coords = "19.847811,-90.535945"

        # Inicializar el contenido del Popup
        content = BoxLayout(orientation="vertical", size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))  # Ajustar tamaño dinámico

        # Generar la información de cada viaje
        for i in range(len(optimized_route) - 1):
            origin_idx = optimized_route[i]
            destination_idx = optimized_route[i + 1]

            # Determinar origen
            if i == 0:  # El primer viaje siempre inicia desde el punto fijo
                origin_name = start_point_name
                origin_coords = start_point_coords
            else:
                origin_name = f"{self.available_localidades[origin_idx-1][1]}, {self.available_localidades[origin_idx-1][0]}"
                origin_coords = "{},{}".format(
                    self.available_localidades[origin_idx-1][2],
                    self.available_localidades[origin_idx-1][3]
                )

            # Determinar destino
            destination_name = f"{self.available_localidades[destination_idx-1][1]}, {self.available_localidades[destination_idx-1][0]}"
            destination_coords = "{},{}".format(
                self.available_localidades[destination_idx-1][2],
                self.available_localidades[destination_idx-1][3]
            )

            # Llamar a la API Directions para obtener distancia y duración
            params = {
                'origin': origin_coords,
                'destination': destination_coords,
                'key': api_key,
                'mode': 'driving',
            }
            url = "https://maps.googleapis.com/maps/api/directions/json"
            response = requests.get(url, params=params)
            data = response.json()

            if data['status'] == 'OK':
                leg = data['routes'][0]['legs'][0]  # Información del primer trayecto
                distance = leg['distance']['text']
                duration = leg['duration']['text']
            else:
                distance = "N/A"
                duration = "N/A"

            # Cantidad de entrega
            delivery_amount = self.available_localidades[destination_idx-1][4]

            # Agregar información del viaje al popup
            content.add_widget(Label(
                text=f"Viaje {i + 1}:\n"
                    f"De: {origin_name} ({origin_coords})\n"
                    f"A: {destination_name} ({destination_coords})\n"
                    f"Distancia: {distance}\n"
                    f"Duración: {duration}\n"
                    f"Unidades a entregar: {delivery_amount}\n",
                size_hint_y=None,
                height=150
            ))

        # Crear el ScrollView para el contenido del Popup
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(content)

        # Crear y abrir el Popup
        popup = Popup(
            title="Detalles de la Ruta",
            content=scroll_view,
            size_hint=(0.9, 0.9),
        )
        popup.open()

    def load_states(self, dropdown):
        try:
            sql = "SELECT DISTINCT estado FROM CCT"
            states = execute_query(sql)
            for state in states:
                state_name = state[0]
                btn = Button(text=state_name, size_hint_y=None, height=44)
                btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                dropdown.add_widget(btn)
        except Exception as e:
            print(f"Error loading states: {e}")

    def open_dropdown(self, button):
        dropdown = DropDown()
        self.load_states(dropdown)
        dropdown.open(button)
        dropdown.bind(on_select=lambda instance, x: self.update_state_selection(button, x))

class MainApp(App):
    def build(self):
        return EquipamientoScreen()

if __name__ == '__main__':
    MainApp().run()
