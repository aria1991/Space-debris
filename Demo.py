import csv
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import poliastro
import urllib

# Retrieve data from satellite tracking database
url = "https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/25544/orderby/EPOCH%20desc/format/tle"
response = urllib.request.urlopen(url)
data = response.read()
text = data.decode("utf-8")

# Parse data into a pandas DataFrame
df = pd.read_csv(StringIO(text), delimiter="\n", header=None, names=["tle"])
df[["tle1", "tle2"]] = df["tle"].str.split("\n", expand=True)
df = df.drop(columns="tle")
df[["sat_name", "sat_num", "classification", "launch_year", "launch_num", "launch_piece", "epoch_year", "epoch_day", "mean_motion_dt2", "mean_motion_ddt6", "bstar", "ephemeris_type", "element_number"]] = df["tle1"].str.split(" ", expand=True, n=11)
df[["inclination", "right_ascension", "eccentricity", "arg_perigee", "mean_anomaly", "mean_motion", "rev_number"]] = df["tle2"].str.split(" ", expand=True, n=6)

# Convert epoch year and day to a single datetime
df["epoch"] = pd.to_datetime(df["epoch_year"] + " " + df["epoch_day"], format="%y %j")

# Calculate positions of all space debris using poliastro
positions = []
for i in range(df.shape[0]):
    r, v = poliastro.tle.propagate(df["tle1"][i], df["tle2"][i], epoch=df["epoch"][i])
    lat, lon, alt = poliastro.ecef_to_geodetic(r[0], r[1], r[2])
    positions.append((lat, lon))

# Visualize positions on a map
plt.figure(figsize=(8, 8))

# Create the map
m = Basemap(projection="ortho", lat_0=lat, lon_0=lon, resolution="l")
m.drawcoastlines(linewidth=0.25)
m.drawcountries(linewidth=0.25)
m.fillcontinents(color="#FFDDCC", lake_color="#DDEEFF")
m.drawmapboundary(fill_color="#DDEEFF")

# Plot the positions of the space debris
for position in positions:
    lat, lon = position
    x, y = m(lon, lat)
    m.plot(x, y, "bo", markersize=6)
