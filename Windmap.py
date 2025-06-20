import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import imageio.v3 as iio
import os
import numpy as np
import pandas as pd
from shapely.geometry import Point
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
import matplotlib.ticker as mticker
from io import BytesIO

# ========== 1. Load Wind Data ==========
nc_file = 'data_stream-oper_stepType-instant.nc'
ds = xr.open_dataset(nc_file)

u10 = ds['u10']
v10 = ds['v10']
lat = ds['latitude'].values
lon = ds['longitude'].values
time = pd.to_datetime(ds['valid_time'].values)

if lat[0] > lat[-1]:
    u10 = u10[:, ::-1, :]
    v10 = v10[:, ::-1, :]
    lat = lat[::-1]

# ========== 2. Load and Prepare India Boundary ==========
india = gpd.read_file("India_Boundary.geojson")
india = india.to_crs("EPSG:4326")

LON, LAT = np.meshgrid(lon, lat)
points = gpd.GeoSeries([Point(xy) for xy in zip(LON.ravel(), LAT.ravel())], crs="EPSG:4326")
mask = points.within(india.unary_union)
mask_2d = np.reshape(mask.to_numpy(), LON.shape)

# ========== 3. In-Memory GIF Setup ==========
gif_path = 'wind_streamlines_india_black.gif'
frames = []

cmap = get_cmap('viridis')
norm = Normalize(vmin=0, vmax=20)

# ========== 4. Generate and Collect Frames (Optimized Step) ==========
for i in range(0, len(time), 12):  # Sample every 6 hours instead of every 1 hour
    u = u10.isel(valid_time=i).values
    v = v10.isel(valid_time=i).values
    speed = np.sqrt(u**2 + v**2)

    u = np.where(mask_2d, u, np.nan)
    v = np.where(mask_2d, v, np.nan)
    speed = np.where(mask_2d, speed, np.nan)

    fig = plt.figure(figsize=(10, 12), facecolor='black')
    ax = plt.axes(projection=ccrs.PlateCarree(), facecolor='black')
    ax.set_extent([68, 98, 6, 38], crs=ccrs.PlateCarree())
    ax.coastlines(color='gray', linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, edgecolor='gray', linewidth=0.3)
    india.boundary.plot(ax=ax, edgecolor='white', linewidth=1)

    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='white', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'color': 'white'}
    gl.ylabel_style = {'color': 'white'}
    gl.xlocator = mticker.FixedLocator(np.arange(68, 99, 5))
    gl.ylocator = mticker.FixedLocator(np.arange(6, 39, 5))

    strm = ax.streamplot(
        lon, lat, u, v,
        color=speed,
        linewidth=1.4,
        cmap=cmap,
        density=4.0,
        norm=norm,
        arrowsize=1,
        integration_direction='both'
    )

    cb = fig.colorbar(strm.lines, ax=ax, orientation='horizontal', pad=0.05, aspect=50)
    cb.set_label('Wind Speed (m/s)', color='white')
    cb.ax.xaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cb.ax.axes, 'xticklabels'), color='white')

    timestamp = time[i].strftime('%Y-%m-%d %H:%M')
    ax.set_title(f'Wind Streamlines over India\n{timestamp}', fontsize=14, color='white')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor=fig.get_facecolor())
    buf.seek(0)
    frames.append(iio.imread(buf))
    buf.close()
    plt.close()

# ========== 5. Write GIF from In-Memory Frames ==========
iio.imwrite(gif_path, frames, duration=1.5, loop=0)
print(f"✅ Optimized Wind Streamline GIF created: {gif_path}")
