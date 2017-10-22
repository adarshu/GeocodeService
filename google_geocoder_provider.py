# Copyright Adarsh Uppula, 2017
#
# This program provides a REST-based Geocoding service to resolve addresses to latitude, longitude coordinates
#
#
import json
import logging
import urllib.request
from urllib.error import URLError
from urllib.parse import quote, urlencode

from geocode_provider import GeocodeProvider
from lat_lng import LatLng


class MyException(Exception):
    """Raise for my specific kind of exception"""

    def __init__(self, message):
        self.message = message


class GoogleGeocoderProvider(GeocodeProvider):
    """ Goecoder using Google Maps service"""
    # if google API changes, update this class

    base_geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"

    def __init__(self, api_key):
        self.api_key = api_key
        self.timeout = 500

    def set_timeoout(self, timeout):
        """Connection or read timeout"""
        self.timeout = timeout

    # geocode
    def geocode_address(self, address):
        try:
            # input validate
            url_params = urlencode({"key": self.api_key, "address": address})
            url_to_call = self.base_geocoding_url + "?%s" + url_params
            url_stream = urllib.request.urlopen(url_to_call, None, self.timeout)
            http_resp_str = url_stream.read()
            json_resp = json.loads(http_resp_str)
            print(json_resp)

            # we consider result valid if it follows the following expected format
            # return the first location found
            lat_lng = None
            if json_resp["results"] is not None:
                if len(json_resp["results"]) == 0:
                    logging.info('No latlng found')
                elif json_resp["results"][0]["geometry"] is not None and json_resp["results"][0]["geometry"]["location"] is not None:
                    json_location = json_resp["results"][0]["geometry"]["location"]
                    lat_lng = LatLng(json_location["lat"], json_location["lng"])
            else:
                raise MyException("Unexpected provider response")
            return lat_lng
        except ValueError:
            logging.error('JSON parsing error')
            raise MyException("JSON parsing error")
        except (URLError) as error:
            logging.error('Data of %s not retrieved because %s\nURL: %s', error.name, error, error.url)
            raise MyException("URLError")
