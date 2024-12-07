import os, sys
import sumolib
import traci
import time
import pandas as pd
import xml.etree.ElementTree as ET
import traci.constants

median_income = 2077892
hours_in_a_month = 30 * 8
hourly_rate = median_income / hours_in_a_month
secondary_rate = hourly_rate / 3600
toll = 30
toll_to_time = toll / secondary_rate
print(toll)

tree = ET.parse('yeoksam_district.xml')
root = tree.getroot()

tazlist = []
for taz in root.iter("taz"):
        for taz_sink in taz.findall("tazSink"):
            tazlist.append(taz_sink.get("id"))

