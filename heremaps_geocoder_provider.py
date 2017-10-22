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


class HeremapsGeocoderProvider(GeocodeProvider):
    """ Goecoder using Here maps service"""
    # if google API changes, update this class

    base_geocoding_url = "https://geocoder.api.here.com/6.2/geocode.json"

    def __init__(self, app_id, app_code):
        self.app_id = app_id
        self.app_code = app_code

    def get_name(self):
        return "HeremapsGeocoder"

    # geocode
    def geocode_address(self, address):
        try:
            # input validate
            url_params = urlencode({"app_id": self.app_id, "app_code": self.app_code, "searchtext": address})
            url_to_call = self.base_geocoding_url + "?" + url_params
            url_stream = urllib.request.urlopen(url_to_call, None, self.timeout)
            json_resp = json.loads(url_stream.read())
            logging.debug("json resp: " + str(json_resp))

            # we consider result valid if it follows the following expected format
            # return the first location found
            lat_lng = None
            if json_resp.get("Response", None):
                if len(json_resp["Response"]) == 0:
                    logging.info('No latlng found')
                elif json_resp["Response"]["View"] and len(json_resp["Response"]["View"]) > 0:
                    json_location = json_resp["Response"]["View"][0]["Result"][0]["Location"]["NavigationPosition"][0]
                    lat_lng = LatLng(json_location["Latitude"], json_location["Longitude"])
            else:
                raise MyException("Unexpected provider response")
            return lat_lng
        except ValueError as error:
            logging.error('Value error: ' + str(error))
            raise MyException("Value error")
        except URLError as error:
            logging.error('URL error: %s', error.reason)
            raise MyException("URLError")
