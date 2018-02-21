import datetime
import numpy as np
import pandas as pd

import matplotlib.pylab as plt
plt.style.use('ggplot')

df_sensors = pd.read_csv("./sensors.csv")
df_sensors.timestamp = pd.to_datetime(df_sensors.timestamp)
df_sensors.timestamp = df_sensors.timestamp.apply(lambda d: d + datetime.timedelta(hours=10))
df_sensors.timestamp = df_sensors.timestamp.apply(lambda d: datetime.datetime(2017, d.month, d.day, d.hour, d.minute))
df_sensors = df_sensors.set_index("timestamp").sort_index().resample("60Min").mean()

df_shading = pd.read_csv("./Shading/df.csv")
df_shading.datetime = pd.to_datetime(df_shading.datetime)
df_shading = df_shading.set_index("datetime").sort_index().resample("60Min").mean()

df_lighting = pd.read_csv("./Lighting/df.csv")
df_lighting.timestamp = pd.to_datetime(df_lighting.timestamp)
df_lighting = df_lighting.set_index("timestamp").sort_index().resample("60Min").mean()

df_aq = pd.read_csv("./AirQuality/df.csv")
df_aq.timestamp = pd.to_datetime(df_aq.timestamp)
df_aq = df_aq.set_index("timestamp").sort_index().resample("60Min").mean()

df = pd.concat([df_sensors.loc["2017-2-10":"2017-4-10"],
                df_shading.loc["2017-2-10":"2017-4-10"],
                df_lighting.loc["2017-2-10":"2017-4-10"]], 
                axis=1)\
                .drop([col for col in df_sensors if col.endswith("min") or col.endswith("max")], axis=1)\
                .drop(["boardid", "boardtype", "elevation", "Position"], axis=1)
df["timestamp"] = df.index.values

#plt.figure(figsize=(15,6))
#plt.title("Temperature [Celsius]")
#df.temp_avg.plot()
#plt.savefig("temperature.png")
#       
#sensors_cols = ["temp_avg", "humidity_avg", "light_avg", "occupancy"]
#actuators_cols = ["angle", "n_lights", "light_avg"]
#
#class SensorStream (object):
#    def __init__ (self, code, s):
#        self.code = code
#        self.s = s
#        self.index = 0
#    def read_next (self):
#        value = self.s.iloc[self.index].values[0]
#        self.index += 1
#        return value

