import json
import urllib.error
import urllib.parse
import urllib.request

from config import LOCATION_RETRIEVAL_URL, OPEN_WEATHER_MAP_API_KEY

# different states for music
WEATHER_STATE_CLEAR = 0
WEATHER_STATE_RAIN = 1
WEATHER_STATE_SNOW = 2

# returns tuple with latitude, longitude
# might return None if failure
def getLocation():

  req = urllib.request.urlopen(LOCATION_RETRIEVAL_URL)
      
  if req.getcode() != 200:
    return
      
  data = req.read()
      
  parsed = json.loads(data)
      
  return (parsed['latitude'], parsed['longitude'], )

# returns tuple with state descriptor (see open weather map), and icon url
# might return None if an error occurs (e.g. the api key is incorrect)
def getCurrentWeatherState(latitude, longitude):
  # composing the OpenWeatherMap url query
  query = {
    'lat': latitude,
    'lon': longitude,
    'APPID': OPEN_WEATHER_MAP_API_KEY
  }
    
  url = urllib.parse.urlunparse((
    'https',
    'api.openweathermap.org',
    'data/2.5/weather',
    '',
    urllib.parse.urlencode(query),
    '',
  ))
    
  # contacting the open weather map server
    
  try:
    req = urllib.request.urlopen(url)
      
    data = req.read()
      
    parsed = json.loads(data)

    return (
      parsed['weather'][0]['main'],
      'https://openweathermap.org/img/wn/{icon}@2x.png'.format(icon=parsed['weather'][0]['icon']),
    )

  except urllib.error.HTTPError:
    return None

def getClearStates():
  return (
    'Clouds',
    'Clear',
    'Mist',
    'Smoke',
    'Haze',
    'Dust',
    'Fog',
    'Sand',
    'Ash',
    'Squall',
  )

def getRainStates():
  return (
    'Rain',
    'Drizzle',
    'Tornado',
    'Thunderstorm',
  )

def getSnowStates():
  return (
    'Snow',
  )
