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


class HeremapsGeocodeProvider(GeocodeProvider):
    """Goecode provider using Here service.

   Attributes:
       app_id: Here maps app id.
       app_code: Here maps app code.
   """

    _base_geocoding_url = "https://geocoder.api.here.com/6.2/geocode.json"

    def __init__(self, app_id, app_code):
        super().__init__()
        self.app_id = app_id
        self.app_code = app_code

    def get_name(self):
        return "HeremapsGeocoder"

    def get_geocode(self, address):
        try:
            url_params = urlencode({"app_id": self.app_id, "app_code": self.app_code, "searchtext": address})
            url_to_call = '%s?%s' % (self._base_geocoding_url, url_params)
            url_stream = urllib.request.urlopen(url_to_call, None, self.timeout)
            json_resp = json.loads(url_stream.read())
            logging.debug("json resp: " + str(json_resp))

            # we consider result valid if it follows the following expected format
            # return the first location found
            lat_lng = None
            if "Response" in json_resp:
                if not json_resp["Response"]["View"]:
                    logging.info('No latlng found')
                elif json_resp["Response"]["View"][0]["Result"]:
                    json_location = json_resp["Response"]["View"][0]["Result"][0]["Location"]["NavigationPosition"][0]
                    lat_lng = LatLng(json_location["Latitude"], json_location["Longitude"])
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
