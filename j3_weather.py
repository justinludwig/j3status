# -*- coding: utf-8 -*-
"""
Display current conditions from openweathermap.org.

As of 2015-10-09, you need to signup for a free API key via
    http://openweathermap.org/register
Once you signup, use the API key generated at signup to either:
1. set the `apikey` parameter directly
2. place the API key (and nothing else) as a single line in
   ~/.config/i3status/openweathermap-apikey
3. same as 2), but at any file location configured via the `apikey_file` parameter

Configuration parameters:
    - apikey : openweathermap.org api key (default: empty)
    - apikey_file : path to file containing api key (default: ~/.config/i3status/openweathermap-apikey)
    - cache_timeout : seconds between requests for weather updates (default: 1800)
    - direction_precision : wind direction precision (default: 2)
        - 1 : N E S W
        - 2 : N NE E SE S etc
        - 3 : N NNE NE ENE E etc
    - format : display format (default: '{city} {temp}°F {icon} {sky} {humidity}%rh {pressure}inHg {direction} {wind}mph')
        - corresponding metric format would be '{city} {temp}°C {icon} {sky} {humidity}%rh {pressure}hPa {direction} {wind}m/s'
        - city : city name (eg 'Seattle')
        - temp : temperature (eg '35')
        - icon : weather icon (eg '☀')
        - sky : weather conditions (eg 'Clear' or 'Rain' or 'Haze' etc)
        - humidity : relative humidity (eg '50')
        - pressure : barometric pressure (eg '29.58')
        - direction : wind direction (eg 'NW')
        - wind : wind speed (eg '11')
    - location : city,country of location for which to show weather (default: 'Seattle,US')
        - see http://openweathermap.org/city
        - for US, a location like 'Springfield IL' will also work
    - request_timeout : seconds after which to abort request (default: 10)
    - timezone : timezone of location (default: 'America/Los_Angeles')
        - used to determine if it's currently day or night at the location
    - units : imperial or metric units (default: 'imperial')
        - imperial :
            - temperature : fahrenheit
            - pressure : inches of mercury
            - wind : miles per hour
        - metric :
            - temperature : celsius
            - pressure : hectopascal
            - wind : meters per second
"""

from datetime import datetime
from dateutil import tz
from os.path import expanduser
from time import time
import json
import requests

DIRECTIONS = {
    1: 'N E S W'.split(),
    2: 'N NE E SE S SW W NW'.split(),
    3: 'N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW'.split(),
}

class Py3status:
    # available configuration parameters

    # literal api key
    apikey = ''
    # or path to file containing api key
    apikey_file = '~/.config/i3status/openweathermap-apikey'

    # check for updates every 1800 seconds (30 minutes)
    cache_timeout = 1800
    # at most 2 direction chars (ie NW)
    direction_precision = 2
    # format as Seattle 50°F ☽ Clear 62%rh 30.25inHg N 5mph
    format = '{city} {temp}°F {icon} {sky} {humidity}%rh {pressure}inHg {direction} {wind}mph'
    #format = '{city} {temp}°C {icon} {sky} {humidity}%rh {pressure}hPa {direction} {wind}m/s'
    # icons
    icon_sun = '☀'
    icon_moon = '☽'
    icon_clouds = '☁'
    icon_rain = '☔'
    icon_fog = '▒'
    icon_mist = '░'
    icon_haze = '☼' # ◌|☷
    icon_snow = '❄'
    icon_thunderstorm = '⚡'
    icon_unknown = '?'
    # get weather for Seattle,US
    location = 'Seattle,US'
    # abort request after 10 seconds
    request_timeout = 10
    # use Pacific Time for calculating day/night
    timezone = 'America/Los_Angeles'
    #timezone = tz.tzlocal()
    # use imperial units instead of metric
    units = 'imperial'

    test_data = ''#'/home/justin/able/weather.json'

    def _load_apikey(self):
        with open(expanduser(self.apikey_file)) as f:
            return f.readline().rstrip()

    def _get_weather(self):
        if self.test_data != '':
            with open(self.test_data) as f:
                return json.load(f)

        apikey = self.apikey or self._load_apikey()
        url = (
            'http://api.openweathermap.org/data/2.5/weather' +
            '?q={location}&units={units}&APPID={apikey}'
        ).format(location=self.location, units=self.units, apikey=apikey)
        response = requests.get(url, timeout=self.request_timeout)

        if response.status_code != 200:
            raise Exception('{status} error getting weather for {location}'.format(
                status=response.status_code, location=self.location))

        return response.json()

    def _get_hour_of_day(self, timestamp):
        dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=tz.tzutc())
        return dt.astimezone(tz.gettz(self.timezone)).hour

    def _get_icon(self, weather):
        sky = weather['weather'][0]['main']

        if sky == 'Clear':
            # after midnight utc, openweathermap.org will report
            # sunrise/sunset for tomorrow
            # so convert to hour of day in order to compare to now
            now = self._get_hour_of_day(int(weather['dt']))
            sunrise = self._get_hour_of_day(int(weather['sys']['sunrise']))
            sunset = self._get_hour_of_day(int(weather['sys']['sunset']))

            if now < sunrise or now > sunset:
                return self.icon_moon
            else:
                return self.icon_sun

        elif sky == 'Clouds': return self.icon_clouds
        elif sky == 'Rain': return self.icon_rain
        elif sky == 'Fog': return self.icon_fog
        elif sky == 'Mist': return self.icon_mist
        elif sky == 'Haze': return self.icon_haze
        elif sky == 'Snow': return self.icon_snow
        elif sky == 'Thunderstorm': return self.icon_thunderstorm

        return icon_unknown

    def _get_temp(self, weather):
        temp = float(weather['main']['temp'])
        return '{:.0f}'.format(temp)

    def _get_pressure(self, weather):
        pressure = float(weather['main']['pressure'])
        if self.units == 'imperial':
            return '{:.2f}'.format(pressure*0.0295) # convert from hPa to inHg
        return '{:.0f}'.format(pressure)

    def _get_wind(self, weather):
        wind = float(weather['wind']['speed'])
        return '{:.0f}'.format(wind)

    def _get_direction(self, weather):
        azimuth = float(weather['wind']['deg'])
        directions = DIRECTIONS[self.direction_precision]
        slices = len(directions)
        slice = 360 / slices
        return directions[int((azimuth+(slice/2))/slice) % slices]

    def j3_weather(self, i3s_output_list, i3s_config):
        weather = self._get_weather()

        text = self.py3.safe_format(self.format, {
            'city': weather['name'],
            'icon': self._get_icon(weather),
            'sky': weather['weather'][0]['main'],
            'temp': self._get_temp(weather),
            'humidity': weather['main']['humidity'],
            'pressure': self._get_pressure(weather),
            'wind': self._get_wind(weather),
            'direction': self._get_direction(weather),
        })

        return {
            'cached_until': time() + self.cache_timeout,
            'full_text': text,
        }

if __name__ == "__main__":
    """
    Test this module by calling it directly.
    """
    from time import sleep
    x = Py3status()
    config = {
        'color_good': '#00FF00',
        'color_degraded': '#FFFF00',
        'color_bad': '#FF0000',
    }
    print(x.j3_weather([], config)['full_text'])
