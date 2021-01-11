
# python globe-cartopy-1.py 65 30
# python globe-hilit-3.py 65 35 > countries.txt
# python globe-anim-1.py

import matplotlib.pyplot as plt
import cartopy.crs as cr
import cartopy.feature as cf
import cartopy.io.shapereader as sh
import shapely.wkt as wkt
import numpy as np
import string
from shapely.geometry import Point
from math import sqrt
import os.path
import textwrap
import csv
import sys

# lat = int (sys.argv[1])
# lon = int (sys.argv[2])

csvfile = "paises-per-superficie-3.txt"
paises = []
i = 1
with open (csvfile) as f:
  reader = csv.reader (f,delimiter='\t')
  for row in reader:
    paises.append ((row [0],row[1],i))
    i += 1
# print (paises)

shpfilename = sh.natural_earth (
  resolution='50m',category='cultural',name='admin_0_countries')
reader = sh.Reader (shpfilename)
countries = list (reader.records())
pngs = []

def find_coords (ct):
  geom = wkt.loads (str (ct.geometry))
  pt = geom.centroid
  lat = pt.y
  lon = pt.x
  return lat,lon

def paint_rotating (lat,lon):
  pngfile = f"png/rot_{lat:.3f}_{lon:.3f}.png"
  if not os.path.isfile (pngfile):
    plt.close('all')
    plt.figure (figsize=(6,6))
    proj = cr.Orthographic(central_latitude=lat,central_longitude=lon)
    ax = plt.axes (projection=proj)
    ax.stock_img ()
    ax.add_feature (cf.LAND)
    ax.add_feature (cf.OCEAN)
    ax.add_feature (cf.COASTLINE)
    ax.add_feature (cf.BORDERS)
    ax.add_feature (cf.LAKES, alpha=0.5)
    ax.add_feature (cf.RIVERS)
    ax.gridlines (color='white', alpha=0.5)
    print ("Writing:", pngfile)
    plt.savefig (pngfile)
  pngs.append (pngfile)

def paint_country (ct,pais):
  # print (ct.attributes['ADM0_A3'], end=" ")
  # print (ct.attributes['ADM0_A3'] + "\t" +  ct.attributes['NAME_LONG'])
  plt.close('all')
  name = pais[1].lower().replace(" ","-")
  printable = set(string.printable)
  name = ''.join(filter(lambda x: x in printable, name))
  geom = wkt.loads (str (ct.geometry))
  pt = geom.centroid
  lat = pt.y
  lon = pt.x
  pngfile = f"png/{name}_{lat:.3f}_{lon:.3f}.png"
  if not os.path.isfile (pngfile):
    plt.figure (figsize=(6,6))
    proj = cr.Orthographic(central_latitude=lat,central_longitude=lon)
    ax = plt.axes (projection=proj)
    ax.stock_img ()
    ax.add_feature (cf.LAND)
    ax.add_feature (cf.OCEAN)
    ax.add_feature (cf.COASTLINE)
    ax.add_feature (cf.BORDERS)
    ax.add_feature (cf.LAKES, alpha=0.5)
    ax.add_feature (cf.RIVERS)
    ax.add_geometries (ct.geometry,cr.PlateCarree(),
      edgecolor='black',
      facecolor='orange', alpha=0.8, zorder=10
      )
    ax.gridlines (color='white', alpha=0.5)
    ax.annotate(pais[1],             
      xy=(10, 560),  xycoords='figure pixels',
      xytext=(10, 560), textcoords='figure pixels',
      ha="left",
      fontsize=25, 
      )
    if pais[2] > 128:
      ax.annotate("", xy=(pt.x, pt.y),  xycoords='data',
        xytext=(0.61, 0.61), textcoords='axes fraction',
        arrowprops=dict(facecolor='black', shrink=0.05),
        horizontalalignment='right', verticalalignment='top',
        alpha=1.0
        )
    print ("Writing:", pngfile)
    plt.savefig (pngfile)
  for i in range (0,30):
    pngs.append (pngfile)

def seek_country1 (abbr):
  for ct in countries:
    if ct.attributes['ADM0_A3'] == abbr:
      # print (textwrap.fill(str(ct),70))
      paint_country (ct,(abbr,ct.attributes['NAME_LONG'],0))

def seek_country2 (pais):
  for ct in countries:
    if ct.attributes['ADM0_A3'] == pais[0]:
      paint_country (ct,pais)

def seek_country3 (abbr):
  for pais in paises:
    if pais[0] == abbr:
      for ct in countries:
        if ct.attributes['ADM0_A3'] == abbr:
          paint_country (ct,pais)

# start,end = "ATA","RUS"

def seek_country4 (abbr):
  for pais in paises:
    if pais[0] == abbr:
      for ct in countries:
        if ct.attributes['ADM0_A3'] == abbr:
          lat,lon = find_coords (ct)
          return lat,lon

def dist (a,b):
  lat0,lon0 = a
  lat1,lon1 = b
  dy = lat1 - lat0
  dx = lon1 - lon0
  return sqrt (dx*dx + dy*dy)

def diff (a,b):
  lat0,lon0 = a
  lat1,lon1 = b
  dy = lat1 - lat0
  dx = lon1 - lon0
  return dy,dx

def easeInOut (t):
  if t > 0.5: 
    result = 4*((t-1)**3)+1 
  else: 
    result = 4*(t**3);
  return result

def stable (abbr):
  seek_country3 (abbr)

def transit (abbr0,abbr1):
  a = seek_country4 (abbr0)
  b = seek_country4 (abbr1)
  lat0,lon0 = a
  lat1,lon1 = b
  print (lat0,lon0)
  print (lat1,lon1)
  
  dy,dx = diff (a,b)
  print ("dy,dx: ", dy,dx)
  d = dist (a,b)
  frames = d // 8
  # print ("d:",d)
  frames = max (4,frames)
  print ("frames:",frames)
  step = 1.0/frames
  for g in np.arange(0.0, 1.0+step, step):
    g1 = easeInOut (g)
    lat2 = lat0 + g1 * dy 
    lon2 = lon0 + g1 * dx
    paint_rotating (lat2,lon2)
    # print (lat2,lon2)

# lst = 'ATA','RUS','FIN','CHN'
paises.reverse()
# lst = [a for a,b,c in paises[0:60]]
lst = [a for a,b,c in paises]

for start,end in list (zip (lst,lst[1:])):
  print (start,end)
  stable (start)
  transit (start,end)
stable (lst[-1])

with open("mylist.txt","w") as f:
 for p in pngs:
  f.write (f"file '{p}'\nduration 0.1\n")
 f.write (f"file '{p}'\n") 


"""

ffmpeg -y -r 20 -f concat -i mylist.txt -c:v libx264 -pix_fmt yuv420p out.mp4

ffmpeg -y -f concat -i mylist.txt -y -vf fps=10 -crf 22 -threads 2 -preset veryfast video.mp4

ffmpeg -f concat -i textfile -y -vf fps=10 -crf 22 -threads 2 -preset veryfast video.mp4


ffmpeg -y -f concat -i mylist.txt out.mp4

ffmpeg -r:v 30 -i mylist.txt -codec:v libx264 -preset veryslow -pix_fmt yuv420p -crf 28 -an "Penguins.mp4"

"""
