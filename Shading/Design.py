#import os
#os.system("python3.4 azi_alt_pysolar.py")

import sys
sys.path.append("/home/alecioc/Downloads/ICT_for_Buildings/Project/Configuration")

import datetime

import numpy as np
import pandas as pd

import matplotlib.pylab as plt
plt.style.use('ggplot')

from mpl_toolkits.basemap import Basemap

from requirements import shading_requirements
from requirements import n_devices

from research_room import windows

def plot_sunpath (df):
    
    # create instance of basemap
    myMap = Basemap(projection='npstere',\
                    boundinglat=0,\
                    lon_0=180,\
                    resolution='l',\
                    round=True,\
                    suppress_ticks=True)
    
    # set the grid up
    gridX, gridY = 10.0, 15.0
    parallelGrid = np.arange(-90.0, 90.0, gridX)
    meridianGrid = np.arange(-180.0, 180.0, gridY)
    
    # draw parallel and meridian grid
    myMap.drawparallels(parallelGrid, labels=[False,False,False,False])
    myMap.drawmeridians(meridianGrid, labels=[False,False,False,False],\
                        labelstyle='+/-',fmt='%i')
    
    # get basemap plot coordinates
    X, Y = myMap(df.azimuth.values, df.altitude.values)

    # set figure    
    ax = plt.gca()
    fig = ax.figure
    fig.set_size_inches(10, 10)    

    # plot azimuth labels, with a North label.
    ax.text(0.5, 
            1.025, 
            'N', 
            transform=ax.transAxes, 
            horizontalalignment='center', 
            verticalalignment='bottom', 
            size=25)
        
    for deg in np.arange(gridY, 360, gridY):
        x = (1.05 * 0.5 * np.sin(np.deg2rad(deg))) + 0.5
        y = (1.05 * 0.5 * np.cos(np.deg2rad(deg))) + 0.5
        ax.text(x,y,u'%i\N{DEGREE SIGN}'%deg,transform=ax.transAxes,\
                horizontalalignment='center',\
                verticalalignment='center')
    
    # plot map
    myMap.plot(X, Y)
    plt.savefig("sunpath.png")


class ShadingDesign (object):
    
    def __init__ (self):
        
        self.df = pd.read_csv("azi_alt.csv")
        self.df["azimuth"] = -(self.df["azimuth"] + 180.0)
        self.df.datetime = pd.to_datetime(self.df.datetime)
        self.df.datetime = self.df.datetime.apply(lambda d: d + datetime.timedelta(hours=8))
        self.df = self.df.set_index("datetime")
        plot_sunpath(self.df)

    def design_horizontal_shading_device (self, 
                                          window, 
                                          device_number,
                                          requirements):
        
        self.device_depth = window["height"]/device_number
        self.df["orientation"] = window["orientation"]
        self.df["hsa"] = self.df["azimuth"] - self.df["orientation"]
        
        self.shade_needed_index = self.df.loc[(self.df.altitude > 0)\
                                            & (self.df.azimuth > -80)\
                                            & (self.df.azimuth < 80)].index

        self.df["vsa"] = 0.0
        self.df.loc[self.shade_needed_index, "vsa"] = \
                           (self.df["altitude"].apply(np.deg2rad).apply(np.tan)\
                           /self.df["hsa"].apply(np.deg2rad).apply(np.cos))\
                           .apply(np.arctan).apply(np.rad2deg)
                           
        
        self.df["h"] = 0                                            
        self.df.loc[self.shade_needed_index, "h"] = \
                   (self.device_depth * self.df["vsa"].apply(np.deg2rad).apply(np.tan))\
                   / (self.df["hsa"].apply(np.deg2rad).apply(np.cos))

        self.df["season"] = ""
        self.df.loc["2017-1-1":"2017-3-21", "season"] = "summer"
        self.df.loc["2017-12-21":"2017-12-31", "season"] = "summer"
        self.df.loc["2017-3-21":"2017-6-21", "season"] = "fall"
        self.df.loc["2017-6-21":"2017-9-21", "season"] = "winter"
        self.df.loc["2017-9-21":"2017-12-21", "season"] = "spring"

        def compute_angle (season, req):
            self.df.loc[self.df.season == season, "gamma"] = \
                        (req * (90.0 - self.df.vsa).apply(np.sin)).apply(np.deg2rad)\
                        .apply(np.arcsin).apply(np.rad2deg)
            self.df.loc[self.df.season == season, "angle"] =\
                       180.0 - (90.0 - self.df.vsa)\
                       - self.df.loc[:, "gamma"]
                        
        for season in ["summer", "winter", "fall", "spring"]:
            compute_angle(season, requirements[season])
            
#        self.df.loc[~self.shade_needed_index, ["gamma","angle"]] = self.df.loc[:, ["gamma","angle"]].fillna(0)
                    
sd = ShadingDesign()
    
sd.design_horizontal_shading_device(windows[0], 
                                    n_devices,
                                    shading_requirements)
df = sd.df

plt.figure(figsize=(15,6))
plt.title("Shade height [m]")
df.h.plot()
plt.savefig("shade_height.png")

plt.figure(figsize=(15,6))
df.h.loc["2017-12-21":"2017-12-31"].plot()
plt.savefig("shade_height_summer_z1.png")

plt.figure(figsize=(15,6))
df.h.loc["2017-1-1":"2017-3-21"].plot()
plt.savefig("shade_height_summer.png")

plt.figure(figsize=(15,6))
df.h.loc["2017-1-1":"2017-3-21"].plot()
plt.savefig("shade_height_winter.png")

plt.figure(figsize=(15,6))
plt.title("Shading device angle [degrees]")
df.angle.plot()
plt.savefig("angle.png")

plt.figure(figsize=(15,6))
df.angle.loc["2017-12-21":"2017-12-31"].plot()
plt.savefig("angle_summer_z1.png")

plt.figure(figsize=(15,6))
df.angle.loc["2017-1-1":"2017-3-21"].plot()
plt.savefig("angle_summer_z2.png")

plt.figure(figsize=(15,6))
plt.title("Shading device angle [degrees] during summer solstice")
df.angle.loc["2017-12-21 00:00":"2017-12-21 23:59"].plot()
plt.savefig("angle_summer_solstice.png")

plt.figure(figsize=(15,6))
df.angle.loc["2017-1-1":"2017-3-21"].plot()
plt.savefig("angle_summer_z2.png")

plt.figure(figsize=(15,6))
plt.title("Shading device angle [degrees] during winter solstice")
df.angle.loc["2017-6-21 00:00":"2017-6-21 23:59"].plot()
plt.savefig("angle_winter_solstice.png")
