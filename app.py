# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)
session = scoped_session(sessionmaker(bind=engine))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    query_recent_date = session.query(func.max(measurement.date)).scalar()
    timeframe_query = pd.to_datetime(query_recent_date) - pd.DateOffset(months=12)
    timeframe_query = timeframe_query.strftime('%Y-%m-$d')
    precipitation_info = session.query(measurement.date, measurement.prcp).filter(measurement.date >= timeframe_query).all()
    precipitation_dict = {}
    for date, prcp in precipitation_info:
        precipitation_dict[date] = prcp
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    count_stations = engine.execute("""SELECT station, count(*) as count from measurement group by station order by count DESC;""")
    desc_stations = [(row['station']) for row in count_stations]
    return jsonify(desc_stations)

@app.route("/api/v1.0/tobs")
def tobs_path():
    query_recent_date = session.query(func.max(measurement.date)).scalar()
    timeframe_query = pd.to_datetime(query_recent_date) - pd.DateOffset(months=12)
    active_station_hist_query = f"""SELECT tobs from measurement where station = 'USC00519281' and date >= '{timeframe_query}'"""
    active_station_hist = pd.read_sql(active_station_hist_query, engine)
    list_active_station = active_station_hist.to_dict(orient='list')
    return jsonify(list_active_station)

@app.route("/api/v1.0/<start>")
def start_date_only(start):
    greater_than_start_query = f"""SELECT min(tobs) as tmin, max(tobs) as tmax, avg(tobs) as tavg from measurement where date >= {start};"""
    greater_than_start = pd.read_sql(greater_than_start_query, engine)
    gts_list = greater_than_start.to_dict(orient='list')
    return jsonify(gts_list)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    start_and_end_query = f"""SELECT min(tobs) as tmin, max(tobs) as tmax, avg(tobs) as tavg from measurement where date between {start} and {end};"""
    bet_start_end = pd.read_sql(start_and_end_query, engine)
    bse_list = bet_start_end.to_dict(orient='list')
    return jsonify(bse_list)

@app.teardown_appcontext
def shut_session_down(exception=None):
    session.remove()



if __name__ == '__main__':
    app.run(debug=True)