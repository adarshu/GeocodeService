# Copyright Adarsh Uppula, 2017
#
# This program provides a REST-based Geocoding service to resolve addresses to latitude, longitude coordinates
#
#
import json
import logging
import urllib.request
from urllib.error import URLError
from urllib.parse import urlencode

from geocode_exception import MyException
from geocode_provider import GeocodeProvider
from lat_lng import LatLng


class GoogleGeocoderProvider(GeocodeProvider):
    """ Goecoder using Google Maps service"""
    # if google API changes, update this class

    base_geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_name(self):
        return "GoogleGeocoder"

    # geocode
    def geocode_address(self, address):
        try:
            # input validate
            url_params = urlencode({"key": self.api_key, "address": address})
            url_to_call = self.base_geocoding_url + "?" + url_params
            url_stream = urllib.request.urlopen(url_to_call, None, self.timeout)
            json_resp = json.loads(url_stream.read())
            logging.debug("json resp: " + str(json_resp))

            # we consider result valid if it follows the following expected format
            # return the first location found
            lat_lng = None
            if json_resp.get("results", None):
                if len(json_resp["results"]) == 0:
                    logging.info('No latlng found')
                elif json_resp["results"][0]["geometry"] and json_resp["results"][0]["geometry"]["location"]:
                    json_location = json_resp["results"][0]["geometry"]["location"]
                    lat_lng = LatLng(json_location["lat"], json_location["lng"])
            else:
                raise MyException("Unexpected provider response")
            return lat_lng
        except ValueError as error:
            logging.error('Value error: ' + str(error))
            raise MyException("Value error")
        except URLError as error:
            logging.error('URL error: %s', error.reason)
            raise MyException("URLError")
