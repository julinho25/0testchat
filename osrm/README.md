# OSRM data

Para desenvolvimento, baixe um recorte pequeno do OpenStreetMap e gere os arquivos `.osrm`.

Exemplo (São Paulo):

```bash
curl -L -o osrm/sample.osm.pbf https://download.geofabrik.de/south-america/brazil/sao-paulo-latest.osm.pbf

docker run -t -v "$(pwd)/osrm:/data" osrm/osrm-backend:v5.27.1 osrm-extract -p /opt/car.lua /data/sample.osm.pbf

docker run -t -v "$(pwd)/osrm:/data" osrm/osrm-backend:v5.27.1 osrm-partition /data/sample.osrm

docker run -t -v "$(pwd)/osrm:/data" osrm/osrm-backend:v5.27.1 osrm-customize /data/sample.osrm
```

Depois suba o `docker-compose`. O serviço `osrm` espera `sample.osrm` dentro da pasta `osrm/`.
