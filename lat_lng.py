# Copyright Adarsh Uppula, 2017
#

class LatLng(object):
    def __init__(self, lat, lng):
        self.latitude = lat
        self.longitude = lng

    @property
    def lat(self):
        return self.latitude

    @lat.setter
    def lat(self, value):
        self.latitude = value

    @property
    def lng(self):
        return self.longitude

    @lng.setter
    def lng(self, value):
        self.longitude = value

    def __eq__(self, other):
        return self.lat == other.lat and self.lng == other.lng

    def __repr__(self):
        return "LatLng: (" + str(self.latitude) + "," + str(self.longitude) + ")"
