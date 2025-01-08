from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import mysql.connector
import requests
from polyline import decode
from simplification.cutil import simplify_coords
from kivy.uix.scrollview import ScrollView
from db_connection import execute_query

class EquipamientoScreen(BoxLayout):

    def reset_screen(self):
        # Añadir aquí la lógica para restablecer todos los elementos necesarios
        # Por ejemplo, si tienes listas o formularios, puedes limpiarlos aquí
        self.ids.algun_id.text = ""  # Resetear texto
        self.ids.otro_id.value = 0   # Resetear valores
        # Puedes también recargar cualquier dato necesario
        self.load_states()  # Suponiendo que este método recargue los datos necesarios

    def go_back(self, instance):
        self.reset_screen()  # Llamar a reset_screen antes de cambiar de pantalla
        # Implementa aquí la funcionalidad deseada, como cerrar la pantalla o navegar al menú principal
        print("Regresando al menú principal...")

    def update_state_selection(self, button, state_name):
        print("Mostrando estados")
        button.text = state_name
        available_ccts = self.get_ccts_by_state(state_name)

        API_KEY = "AIzaSyAZC4UtWCoYayInA-CyzJ4lKso8PcJLtok"  # Reemplaza con tu clave de Google Maps API

        # Convertir las coordenadas a strings "lat,lng"
        original_waypoints = ["{},{}".format(lat, lng) for lat, lng in available_ccts]
        validated_waypoints = []

        # Verificar accesibilidad de cada waypoint
        for waypoint in original_waypoints:
            lat, lng = map(float, waypoint.split(","))
            test_route_url = "https://maps.googleapis.com/maps/api/directions/json"
            
            params = {
                "origin": waypoint,
                "destination": waypoint,
                "key": API_KEY
            }
            response = requests.get(test_route_url, params=params)
            route_data = response.json()

            if route_data["status"] == "OK":
                validated_waypoints.append(waypoint)  # Punto accesible
            else:
                # Encontrar un punto accesible cercano
                places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                lat, lng = map(float, waypoint.split(","))
                radius = 10000

                while radius <= 200000:
                    places_params = {
                        "location": f"{lat},{lng}",
                        "radius": radius,  # Buscar puntos accesibles en un radio de 5 km
                        "key": API_KEY
                    }
                    places_response = requests.get(places_url, params=places_params)
                    places_data = places_response.json()

                    if places_data["status"] == "OK" and places_data["results"]:
                        nearest_place = places_data["results"][0]
                        validated_waypoints.append(f"{nearest_place['geometry']['location']['lat']},{nearest_place['geometry']['location']['lng']}")
                        break
                    radius += 5000
                else:
                    print(f"No se encontró un lugar accesible cercano a {waypoint}. Ignorando este punto.")

        if not validated_waypoints:
            print("No se encontraron puntos accesibles para generar una ruta.")
            return

        # Calcular el centro geográfico
        latitudes = [float(latlng.split(",")[0]) for latlng in validated_waypoints]
        longitudes = [float(latlng.split(",")[1]) for latlng in validated_waypoints]
        centro_lat = sum(latitudes) / len(latitudes)
        centro_lng = sum(longitudes) / len(longitudes)
        centro = f"{centro_lat},{centro_lng}"

        # Calcular nivel de zoom según la dispersión de los puntos
        lat_range = max(latitudes) - min(latitudes)
        lng_range = max(longitudes) - min(longitudes)
        max_range = max(lat_range, lng_range)

        if max_range < 0.05:
            zoom = 14
        elif max_range < 0.1:
            zoom = 12
        elif max_range < 0.5:
            zoom = 10
        else:
            zoom = 8

        # Directions API: calcular la ruta óptima
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": validated_waypoints[0],  # Primer punto como origen
            "destination": validated_waypoints[0],  # Vuelve al primer punto (ruta circular)
            "waypoints": "optimize:true|" + "|".join(validated_waypoints[1:]),  # Optimizar puntos
            "key": API_KEY
        }
        response = requests.get(directions_url, params=params)
        route_data = response.json()

        if route_data["status"] != "OK":
            print(f"Error al calcular la ruta: {route_data['status']}")
            return

        # Procesar las rutas del JSON
        all_coordinates = []
        for leg in route_data["routes"][0]["legs"]:
            for step in leg["steps"]:
                polyline = step["polyline"]["points"]
                decoded_points = decode(polyline)  # Decodificar polyline
                all_coordinates.extend(decoded_points)

        print("-------------------------------------------------------------")
        print(f'All cordinates = {all_coordinates}')

        print("-------------------------------------------------------------")

        # Generar Static Maps URL
        static_map_url = "https://maps.googleapis.com/maps/api/staticmap"

        # Simplificar las coordenadas usando Douglas-Peucker
        tolerance = 0.0005  # Ajusta la tolerancia según el nivel de detalle deseado
        simplified_coordinates = simplify_coords(all_coordinates, tolerance)

        # Formatear las coordenadas como 'lat,lng'
        formatted_coordinates = ["{:.6f},{:.6f}".format(lat, lng) for lat, lng in simplified_coordinates]

        # Parámetro `path` para la ruta optimizada
        path_param = "path=color:blue|weight:10|" + "|".join(formatted_coordinates)

        # Parámetro `markers` para resaltar waypoints con números
        markers_list = [
            f"markers=color:red|label:{i+1}|{validated_waypoints[i]}"
            for i in range(len(validated_waypoints))
        ]
        markers_param = "&".join(markers_list)

        # Parámetros de la solicitud a Static Maps
        static_map_params = {
            "size": "800x600",      # Tamaño de la imagen
            "path": path_param,     # Ruta optimizada
            "center": centro,       # Centro del mapa
            "zoom": zoom,             # Nivel de zoom
            "key": API_KEY,         # Clave de la API
            "markers": markers_param  # Marcadores para los waypoints
        }

        # Concatenar parámetros para incluir marcadores
        static_map_url_with_params = f"{static_map_url}?{'&'.join(f'{key}={value}' for key, value in static_map_params.items())}&{markers_param}"

        # Solicitar Static Maps
        static_map_response = requests.get(static_map_url_with_params)

        # Guardar la imagen
        if static_map_response.status_code == 200:
            with open(f"{state_name}.png", "wb") as file:
                file.write(static_map_response.content)
            self.ids.map_image.source = f"{state_name}.png"
            self.ids.map_image.reload()
            print(f"Imagen guardada como '{state_name}.png'")
        else:
            print(f"Error al generar el mapa: {static_map_response.text}")

        
        # Crear un layout para el contenido del ScrollView
        content = BoxLayout(orientation="vertical", size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))  # Ajustar tamaño dinámico

        print("-------------------------------------------------------------")

        if "routes" in route_data and len(route_data["routes"]) > 0:
            for leg in route_data["routes"][0]["legs"]:
                content.add_widget(Label(text=f"Inicio: {leg['start_address']}", size_hint_y=None, height=40))
                content.add_widget(Label(text=f"Destino: {leg['end_address']}", size_hint_y=None, height=40))
                content.add_widget(Label(text=f"Distancia: {leg['distance']['text']}", size_hint_y=None, height=40))
                content.add_widget(Label(text=f"Duración: {leg['duration']['text']}", size_hint_y=None, height=40))
                content.add_widget(Label(text="----", size_hint_y=None, height=40))
        else:
            #print("No se encontraron rutas.")
            content.add_widget(Label(text="No se encontraron rutas.", size_hint_y=None, height=40))

        print("-------------------------------------------------------------")


        # Crear el ScrollView
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(content)

        # Crear el Popup
        popup = Popup(
            title="Información de la Ruta",
            content=scroll_view,
            size_hint=(0.8, 0.8),
        )

        # Mostrar el Popup
        popup.open()

    def set_image_widget(self, image_path):
        """Actualiza el widget de imagen con el mapa generado."""
        self.map_image.source = image_path
        self.map_image.reload()

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
            print(f"Error al cargar estados: {e}")

    def get_ccts_by_state(self, state):
        try:
            sql = "SELECT claveCentro, nombre, latitud, longitud FROM CCT WHERE estado = ?"
            ccts = execute_query(sql, (state,))
            return [[float(latitud), float(longitud)] for clave, nombre, latitud, longitud in ccts]

        except Exception as e:
            print(f"Error al obtener CCTs: {e}")
            return []
        
    def open_dropdown(self, button):
        dropdown = DropDown()
        self.load_states(dropdown)  # Carga los estados en el dropdown
        dropdown.open(button)
        dropdown.bind(on_select=lambda instance, x: self.update_state_selection(button, x))

class MainApp(App):
    def build(self):
        return EquipamientoScreen().build()

if __name__ == '__main__':
    MainApp().run()