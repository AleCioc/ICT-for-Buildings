import sys
sys.path.append("/home/alecioc/Downloads/ICT_for_Buildings/Project")
sys.path.append("/home/alecioc/Downloads/ICT_for_Buildings/Project/Configuration")

import datetime
import pandas as pd
import numpy as np

import matplotlib.pylab as plt
plt.style.use('ggplot')

from requirements import lighting_requirements

from research_room import floor
from research_room import ceiling
from research_room import wall
from research_room import windows
from research_room import desk

rho_m = (floor["surface"] * floor["rho"]\
 + ceiling["surface"] * ceiling["rho"]\
 + wall["surface"] * wall["rho"])\
 / (floor["surface"] + ceiling["surface"] + wall["surface"])
 
 
for w in windows:
    w["eta"] = w["height"] * w["width"] * w["psi"] * w["epsilon"] * w["tau"]
eta_m = pd.Series([w["eta"] for w in windows]).sum()\
/ ((1.0 - rho_m) * (floor["surface"] + ceiling["surface"] + wall["surface"]))

space_index = (floor["a"]*floor["b"])\
              / ((floor["a"]+floor["b"])*(ceiling["height"] - desk["height"]))


total_flux = (lighting_requirements["Em"] * floor["surface"])\
             / (lighting_requirements["U"] * lighting_requirements["M"])
n_sources = total_flux / lighting_requirements["lumen_output"]

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
  
df["light_power"] = (10.0/df.h).apply(np.log)
df.loc[df.h == 0, "light_power"] = 0
df["light_power"] = 100.0 * (df["light_power"]-df["light_power"].min())\
                      / (df["light_power"].max()-df["light_power"].min())

plt.figure(figsize=(15,6))
plt.title("Natural light sensed vs artificial light dimmer value [V%]")
df.light_avg.plot(label="Sensor")
df.light_power.plot(label="Dimmer")
plt.legend()
plt.savefig("light.png")

df.loc[:,["timestamp","light_power"]].to_csv("df.csv")