# Copyright Adarsh Uppula, 2017
#
import unittest

from google_geocode_provider import GoogleGeocodeProvider
from heremaps_geocode_provider import HeremapsGeocodeProvider
from lat_lng import LatLng


class TestGeocoders(unittest.TestCase):
    def test_gmaps(self):
        google_provider = GoogleGeocodeProvider('AIzaSyB705HK0ZIq9OXlNGY-U4mqNCbnPc2qy8c')
        google_provider.timeout = 3
        google_address = '1600 Amphitheater Parkway, Mountain View'
        self.assertEqual(google_provider.get_geocode(google_address), LatLng(37.4216548, -122.0856374))

    def test_here(self):
        here_provider = HeremapsGeocodeProvider('Rw3fI3JTurwOcIPtrOX9', '2D-7FLXX04a5zDQKnDiT7A')
        here_provider.timeout = 3
        google_address = '1600 Amphitheater Parkway, Mountain View'
        self.assertEqual(here_provider.get_geocode(google_address), LatLng(37.42307, -122.08414))


if __name__ == '__main__':
    unittest.main()
