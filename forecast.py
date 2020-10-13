import argparse
import pickle
import xarray as xr
import pandas as pd
import geopandas as gpd
from siphon.catalog import TDSCatalog

parser = argparse.ArgumentParser()
parser.add_argument("f_day", type=str)
parser.add_argument("l_day", type=str)
p = parser.parse_args()

f_day = pd.to_datetime(p.f_day)
l_day = pd.to_datetime(p.l_day)

targets = ('06005', '06022', '06296', '06027',
           '05004', '05012', '05024', '05805')

def gauges_coords(identifiers):
  asunp = gpd.read_file('http://asunp.meteo.ru/geoits-rest/services/asunp/geo.json', driver='GeoJSON')
  posts = asunp[asunp.gidro.isin(identifiers) & (asunp.ktoCategory.isin(
      ['post_gidro', 'station_gidro']))].sort_values(by=['lon']).set_index('gidro', drop=False)
  return posts
  
def get_weather_forecast(start, end):
  """прогноз погоды GFS
  """
  tz = 'Europe/Moscow'
  forecastvariables = ['Temperature_isobaric', 'Temperature_surface', 'Precipitation_rate_surface']

  gfs_cat = TDSCatalog('http://thredds.ucar.edu/thredds/catalog'
                       '/grib/NCEP/GFS/Global_0p5deg/catalog.xml')
  latest = gfs_cat.latest
  ncss = latest.subset()
  query = ncss.query().variables(*forecastvariables)
  query.time_range(start, end).accept('netCDF4')
  nc = ncss.get_data(query)
  fds = xr.open_dataset(xr.backends.NetCDF4DataStore(nc))  # TODO: try H5NetCDFStore backend
  fds = fds.sel(isobaric6=100000)
  return fds


def is_spring(ds):
    date = pd.to_datetime(ds)
    return (date.month >= 3 and date.month <= 5)


def is_summer(ds):
    date = pd.to_datetime(ds)
    return (date.month >= 6 and date.month <= 9)


def predict(weather_frcst):
  predictions = []
  for identifier in targets:
    point = weather_frcst.sel(lat=gauges.loc[identifier].lat,
                              lon=gauges.loc[identifier].lon,
                              method='nearest'
                              )
    future = point.to_dataframe().reset_index()
    future = future.rename(
        {i: "ds" for i in future.columns if i.startswith("time")}, axis=1)
    future = future.rename({
        'Temperature_surface': 'temperature_ground',
        'Temperature_isobaric': 'temperature_air',
        'Precipitation_rate_surface': 'precipitation_amount'
    }, axis=1)

    future = future.set_index('ds').resample('D')\
        .agg({
            'precipitation_amount': 'sum',
            'temperature_air': 'mean', 'temperature_ground': 'mean'
        })

    future = future.reset_index()
    future['temperature_air'] = future.temperature_air - 273.15
    future['temperature_ground'] = future.temperature_ground - 273.15

    future['spring'] = future['ds'].apply(is_spring)
    future['summer'] = future['ds'].apply(is_summer)

    with open(f'./models/{int(identifier)}.pkl', 'rb') as f:
      forecaster = pickle.load(f)
      forecast = forecaster.predict(future)
      sf = forecast.set_index('ds').yhat.rename('5012')
      predictions.append(sf)

  return predictions


weather_frcst = get_weather_forecast(f_day, l_day)
gauges = gauges_coords(targets)
predictions = predict(weather_frcst)

submission = pd.DataFrame(predictions).T
submission.to_csv('submission.csv')

print(predictions)
