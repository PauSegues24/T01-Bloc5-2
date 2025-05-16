# Arxiu per calcular a temperatura màxima, la mínima i la mitjana de Solsona | Pau Segués Vitutia

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import json
from datetime import datetime
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 41.9939,
	"longitude": 1.5171,
	"hourly": "temperature_2m"
}
responses = openmeteo.weather_api(url, params=params)
# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)


# Codi per a calcular la temperatura màxima, la mínima i la mitjana de Solsona
# Funció per calcular la temperatura màxima (sense .max())
def temperatura_maxima(df):
    max_temp = df["temperature_2m"].iloc[0]
    for t in df["temperature_2m"]:
        if t > max_temp:
            max_temp = t
    return max_temp
# Funció per calcular la temperatura mínima (sense .min())
def temperatura_minima(df):
    min_temp = df["temperature_2m"].iloc[0]
    for t in df["temperature_2m"]:
        if t < min_temp:
            min_temp = t
    return min_temp
# Funció per calcular la temperatura mitjana (sense .mean())
def temperatura_mitjana(df):
    suma = 0
    comptador = 0
    for t in df["temperature_2m"]:
        suma += t
        comptador += 1
    if comptador > 0:
        return suma / comptador
    else:
        return 0
# Calculem les dades
maxima = temperatura_maxima(hourly_dataframe)
minima = temperatura_minima(hourly_dataframe)
mitjana = temperatura_mitjana(hourly_dataframe)
# Guardem les dades en un diccionari
resultats = {
    "temperatura_maxima": maxima,
    "temperatura_minima": minima,
    "temperatura_mitjana": mitjana
}
# Generem el nom del fitxer amb la data actual
data_actual = datetime.now().strftime("%Y%m%d")
nom_fitxer = f"temp_{data_actual}.json"
# Guardem el diccionari en un fitxer .json
with open(nom_fitxer, "w") as fitxer:
    json.dump(resultats, fitxer, indent=4)
print(f"Dades exportades correctament a {nom_fitxer}")
