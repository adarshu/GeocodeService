# Copyright Adarsh Uppula, 2017
#
import json
import logging
import urllib.request
from urllib.error import URLError
from urllib.parse import urlencode

from geocode_exception import GeocodeException
from geocode_provider import GeocodeProvider
from lat_lng import LatLng


class GoogleGeocodeProvider(GeocodeProvider):
    """Goecode provider using Google Maps service.

   Attributes:
       api_key: Google Maps api key.
   """

    _base_geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"  # base url to Google's geocode service

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def get_name(self):
        return "GoogleGeocoder"

    def get_geocode(self, address):
        try:
            url_params = urlencode({"key": self.api_key, "address": address})
            url_to_call = '%s?%s' % (self._base_geocoding_url, url_params)
            url_stream = urllib.request.urlopen(url_to_call, None, self.timeout)
            json_resp = json.loads(url_stream.read())
            logging.debug("json resp: " + str(json_resp))

            # we consider the result valid if it follows the following expected format
            # return the first location found
            lat_lng = None
            if "results" in json_resp:
                if not json_resp["results"]:
                    logging.info('No latlng found')
                elif json_resp["results"][0]["geometry"] and json_resp["results"][0]["geometry"]["location"]:
                    json_location = json_resp["results"][0]["geometry"]["location"]
                    lat_lng = LatLng(json_location["lat"], json_location["lng"])
            else:
                raise GeocodeException("Unexpected provider response")
            return lat_lng
            # catch parsing errors
        except ValueError as error:
            logging.error('Value error: ' + str(error))
            raise GeocodeException("Value error")
        # catch connection errors
        except URLError as error:
            logging.error('URL error: ' + str(error))
            raise GeocodeException("URLError")
