import sys
sys.path.append("/home/alecioc/Downloads/ICT_for_Buildings/Project/Configuration")

from rooms import rooms

import pandas as pd
df = pd.read_csv("df.csv").set_index("datetime")

class Sensor (object):
    def __init__ (self, room_id, conf, df):
        self.room = room_id
        self.conf = conf
        self.df = df
    def read (self):
        pass
        
conf = {
            "code" = "s1"
            "room_code" = rooms["AAA"]["code"]        
            "phy_name":"Ambient light",
            "phy_unit":"Lux",
            "value_type":"analog"
        }

light = Sensor(conf)