# Copyright Adarsh Uppula, 2017
#

class LatLng():
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

    def __repr__(self):
        return "LatLng: (" + str(self.latitude) + "," + str(self.longitude) + ")"
