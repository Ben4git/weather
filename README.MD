in irder to use uWgsi call
uwsgi --socket 127.0.0.1:3031 --wsgi-file views.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191

in order to avoid broken pipes

## Meteotest URLs

> https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_radar&lat=48.4&lon=7.6

> https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts&lat=47&lon=7&start=now&end=+8%20hours

> https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_measurements&wmo=66030&start=-12%20hours&end=now

# Documentation

> https://mdx.meteotest.ch/info/data




# 1st Version

Schlechtes Wetter:
    Regenwahrscheinlichkeit > 50%
    
Schlechtes Wetter:
    Regenwahrscheinlichkeit < 50%
    
    
Ergibt Suchbegriffe:
    Schlechtes Wetter: regen
    Gutes Wetter: sonne
    
    