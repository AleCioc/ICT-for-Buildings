import sys
sys.path.append("/home/alecioc/Downloads/ICT_for_Buildings/Project/Configuration")

import datetime

import pandas as pd
import numpy as np

import matplotlib.pylab as plt
plt.style.use('ggplot')

from requirements import air_quality_requirements
from conference_room import conference_room

f_av_occ = air_quality_requirements["nhs"] / 24.0 * air_quality_requirements["npeople"]
ach_iaq = air_quality_requirements["qiaq"] * f_av_occ / conference_room["volume"]

voc_wall = (conference_room["wall_voc"] * (conference_room["wall_surface"]/(0.9*conference_room["volume"])))\
                      / ach_iaq

voc_floor = (conference_room["floor_voc"] * (conference_room["floor_surface"]/(0.9*conference_room["volume"])))\
                      / ach_iaq

voc_ceiling = (conference_room["ceiling_voc"] * (conference_room["ceiling_surface"]/(0.9*conference_room["volume"])))\
                      / ach_iaq

voc = voc_ceiling + voc_floor + voc_wall

df_sensors = pd.read_csv("../sensors.csv")
df_sensors.timestamp = pd.to_datetime(df_sensors.timestamp)
df_sensors.timestamp = df_sensors.timestamp.apply(lambda d: d + datetime.timedelta(hours=10))
df_sensors.timestamp = df_sensors.timestamp.apply(lambda d: datetime.datetime(2017, d.month, d.day, d.hour, d.minute))
df_sensors = df_sensors.set_index("timestamp").sort_index().resample("60Min").mean()

df_shading = pd.read_csv("../Shading/df.csv")
df_shading.datetime = pd.to_datetime(df_shading.datetime)
df_shading = df_shading.set_index("datetime").sort_index().resample("60Min").mean()

df = pd.concat([df_sensors.loc["2017-2-10":"2017-4-10"],
                df_shading.loc["2017-2-10":"2017-4-10"]], 
                axis=1)\
                .drop([col for col in df_sensors if col.endswith("min") or col.endswith("max")], axis=1)\
                .drop(["boardid", "boardtype", "elevation", "Position"], axis=1)
df["timestamp"] = df.index.values
  
df["occupancy"] = pd.Series(np.random.randint(5,20,size=len(df)), index=df.index)
df.loc[df.timestamp.apply(lambda d:d.hour) < 9, "occupancy"] = np.NaN
df.loc[df.timestamp.apply(lambda d:d.hour) > 18, "occupancy"] = np.NaN
df.loc[df.timestamp.apply(lambda d:d.hour) == 13, "occupancy"] = np.NaN
 
df["f_inst"] = df["occupancy"]
df["iaq_inst"] = air_quality_requirements["qiaq"] * df["f_inst"] / conference_room["volume"]

df["voc_wall"] = (conference_room["wall_voc"] * (conference_room["wall_surface"]/(0.9*conference_room["volume"])))\
                      / df["iaq_inst"]

df["voc_floor"] = (conference_room["floor_voc"] * (conference_room["floor_surface"]/(0.9*conference_room["volume"])))\
                      / df["iaq_inst"]

df["voc_ceiling"] = (conference_room["ceiling_voc"] * (conference_room["ceiling_surface"]/(0.9*conference_room["volume"])))\
                      / df["iaq_inst"]

df["voc"] = (df["voc_ceiling"] + df["voc_floor"] + df["voc_wall"]).fillna(0)
df["ventilation_power"] = df.voc.fillna(0)
df.ventilation_power = df.ventilation_power * df.temp_avg.clip(lower=0.8, upper=1.2)
df.ventilation_power = df.ventilation_power * df.humidity_avg.clip(lower=0.8, upper=1.2)
df["ventilation_power"] = (df.ventilation_power.clip(lower=0, upper=100.0))

plt.figure(figsize=(15,6))
plt.title("Room occupancy [number of people]")
df.occupancy.fillna(0).plot(drawstyle="step")
plt.savefig("occupancy.png")

plt.figure(figsize=(15,6))
plt.title("VOC and ventilation dimmer power")
df.voc.fillna(0).plot(drawstyle="step", label="VOC [micro_g/m3]")
df.ventilation_power.fillna(0).plot(drawstyle="step", label="Ventilation dimmer power [V%]")
plt.legend()
plt.savefig("ventilation_power.png")

df.loc[:,["timestamp", "occupancy", "voc", "ventilation_power"]].to_csv("df.csv")
