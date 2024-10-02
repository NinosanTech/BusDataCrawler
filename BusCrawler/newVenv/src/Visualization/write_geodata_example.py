import geopandas as gpd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from shapely.geometry import LineString
from geoalchemy2 import Geometry
import sys
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# setting path
sys.path.append('../src')
from src.DataCrawler import credentials


Base = declarative_base()

class Auslastung(Base):
    __tablename__ = "occupancy"

    id = Column(Integer, primary_key=True)
    occupancy = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)

class BusConnections(Base):
    __tablename__ = 'bus_connections'

    id = Column(Integer, primary_key=True)
    company = Column(String(100), nullable=False)
    route = Column(Geometry(geometry_type='LINESTRING', srid=4326))  # Hier kannst du auch ein Geometry-Feld verwenden
    occupancy_id = Column(Integer, ForeignKey('occupancy.id'), nullable=False)

# Verbindung zur MySQL-Datenbank herstellen
server='db-mysql-fra1-bus-data-crawler-v1-do-user-17586954-0.d.db.ondigitalocean.com'
username=credentials.dig_ocean_visualizer_username
password=credentials.dig_ocean_visualizer_password
database='visualization'
port = 25060
database_url = f'mysql+mysqlconnector://{username}:{password}@{server}:{port}/{database}'
engine = create_engine(database_url)

Session = sessionmaker(bind=engine)
session = Session()

line = LineString([[-34.6, -58.38], [-31.416668, -64.183334]])
date = datetime.strptime('2024/10/02','%Y/%m/%d')
occupancy = 10
a = Auslastung(occupancy=occupancy, date=date)
session.add(a)
session.commit()

occupancy_id = a.id

b = BusConnections(company='TestCompany', route=line.__str__(), occupancy_id=occupancy_id)
session.add(b)
session.commit()
session.close()


# # Beispiel-GeoDataFrame miteinem Punkt
# data = {
#     'line': 'Buslinie 100',
#     'auslastung': {date: 70},
#     'geometry': [line]
# }

# # GeoDataFrame erstellen
# gdf = gpd.GeoDataFrame(data, geometry='geometry')

# with engine.connect() as conn:
#     # Daten in die Datenbank schreiben
#     gdf.to_wkt().to_sql(
#         'bus_lines', 
#         conn, 
#         if_exists='append', 
#         index=False, 
#         # dtype={'geometry': Geometry('line', srid=4326)}  # Geometrie-Typ und SRID spezifizieren
#         dtype={'geometry': Geometry('LINESTRING', srid=4326)}  # Geometrie-Typ und SRID spezifizieren
#     )
