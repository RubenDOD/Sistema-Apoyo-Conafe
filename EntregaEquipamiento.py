from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
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
import requests
from polyline import decode
from simplification.cutil import simplify_coords
from kivy.uix.scrollview import ScrollView

Window.clearcolor = (1, 1, 1, 1)  # RGB blanco y opacidad completa

class EquipamientoScreen(BoxLayout):

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Título superior
        title = Label(text="Entrega de Equipamiento", size_hint_y=0.1, font_size=24, bold=True, halign="center", color=[0,0,0,1])
        layout.add_widget(title)

        footer = BoxLayout(size_hint_y=0.1)

        state_dropdown = DropDown()
        print("Se cargaran los estados")
        self.load_states(state_dropdown)
        print("Estados cargados correctamente")

        print("Se aplicara un boton por cada estado para cuando se seleccione un estado")
        state_button = Button(text="Seleccionar Estado")
        state_button.bind(on_release=state_dropdown.open)
        state_dropdown.bind(on_select=lambda instance, x: self.update_state_selection(state_button, x))
        footer.add_widget(state_button)
        print("Se configuró correctamente")

        # Botón de regresar
        btn_back = Button(text="Regresar")
        btn_back.bind(on_release=self.go_back)
        footer.add_widget(btn_back)

        layout.add_widget(footer)

        return layout

    def go_back(self, instance):
        # Implementa aquí la funcionalidad deseada, como cerrar la pantalla o navegar al menú principal
        print("Regresando al menú principal...")

    def update_state_selection(self, button, state_name):
        print("Mostrando estados")
        button.text = state_name
        self.map_editor.available_ccts = self.get_ccts_by_state(state_name)
        self.map_editor.selected_state = state_name  # Guardar el estado seleccionado

        API_KEY = "AIzaSyAZC4UtWCoYayInA-CyzJ4lKso8PcJLtok"  # Reemplaza con tu clave de Google Maps API

        # Convertir las coordenadas a strings "lat,lng"
        original_waypoints = ["{},{}".format(lat, lng) for lat, lng in self.map_editor.available_ccts]
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

        # Parámetro `markers` para resaltar waypoints
        markers_param = "markers=color:red|size:mid|" + "|".join(validated_waypoints)

        # Parámetros de la solicitud a Static Maps
        static_map_params = {
            "size": "800x600",      # Tamaño de la imagen
            "path": path_param,     # Ruta optimizada
            "center": centro,       # Centro del mapa
            "zoom": 8,             # Nivel de zoom
            "key": API_KEY,         # Clave de la API
            "markers": markers_param  # Marcadores para los waypoints
        }

        # Solicitar Static Maps
        static_map_response = requests.get(static_map_url, params=static_map_params)

        # Guardar la imagen
        if static_map_response.status_code == 200:
            with open(f"{state_name}.png", "wb") as file:
                file.write(static_map_response.content)
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
        self.map_image = Image(
            source=image_path,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )

    def set_image(self, selection, popup):
        if selection:
            self.set_image_widget(selection[0])
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
        cursor.execute("SELECT claveCentro, nombre, latitud, longitud FROM CCT WHERE estado = %s", (state,))
        ccts = cursor.fetchall()
        conn.close()
        return [[float(latitud),float(longitud)] for clave, nombre, latitud, longitud in ccts]
        #return [[f"{clave} ({nombre})",(float(latitud),float(longitud))] for clave, nombre, latitud, longitud in ccts]

class MainApp(App):
    def build(self):
        return EquipamientoScreen().build()

if __name__ == '__main__':
    MainApp().run()