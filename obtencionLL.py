import pandas as pd
import requests

def obtener_coordenadas_localidades(api_key, filename):
    # Cargar el archivo Excel
    data = pd.read_excel(filename)
    
    # Diccionario para almacenar las coordenadas
    localidades_coords = []

    for _, row in data.iterrows():
        # Construir la consulta a la API de Google Maps Geocoding
        query = f"{row['LOCALIDAD']}, {row['MUNICIPIO']}, Campeche, Mexico"
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={api_key}"

        # Realizar la solicitud
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result['results']:
                location = result['results'][0]['geometry']['location']
                localidades_coords.append({
                    'Municipio': row['MUNICIPIO'],
                    'Localidad': row['LOCALIDAD'],
                    'Latitud': location['lat'],
                    'Longitud': location['lng']
                })
            else:
                localidades_coords.append({
                    'Municipio': row['MUNICIPIO'],
                    'Localidad': row['LOCALIDAD'],
                    'Latitud': None,
                    'Longitud': None
                })
        else:
            localidades_coords.append({
                'Municipio': row['MUNICIPIO'],
                'Localidad': row['LOCALIDAD'],
                'Latitud': None,
                'Longitud': None
            })

    # Convertir la lista a DataFrame
    localidades_df = pd.DataFrame(localidades_coords)
    
    # Guardar en un nuevo archivo CSV
    localidades_df.to_csv('Coordenadas_Localidades_Campeche.csv', index=False)

    return localidades_df

# Uso del código:
# Llamar a la función con tu clave de API y el nombre del archivo
api_key = "AIzaSyAZC4UtWCoYayInA-CyzJ4lKso8PcJLtok"
filename = "Campeche_por_municipio.xlsx"
coordenadas_df = obtener_coordenadas_localidades(api_key, filename)
print(coordenadas_df)
