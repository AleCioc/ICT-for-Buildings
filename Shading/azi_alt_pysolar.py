#Python3.4

import os
import os.path
if os.path.isfile("./azi_alt.csv"):
	os.remove("./azi_alt.csv")
with open("azi_alt.csv","a+") as data:
	data.write("datetime,altitude,azimuth\n")

import sys
sys.path.append("/home/alecioc/Downloads/ICT_for_Buildings/Project")
from conf import geo_info

latitude = geo_info["lat"]
longitude = geo_info["lon"]

import datetime

from pysolar.solar import *

for month in range(1,13):
    for day in range(1,32):
        for hour in range(0,24):
            for minute in range(0, 60, 5):
                try:
                    d = datetime.datetime(2017, month, day, hour, minute, 0, 0)
                    altitude = get_altitude(latitude, longitude, d)
                    azimuth = get_azimuth(latitude, longitude, d)
                    with open("azi_alt.csv","a+") as data:
                        data.write(str(d) + "," + str(altitude) + "," + str(azimuth) + "\n")
                except:
                    pass
