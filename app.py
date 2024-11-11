# Import the dependencies.
import numpy as np

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """welcome to Hawaii weather API, heres are the following routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitaion data fro the last 12 months<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temp of the most active station for last 12 months<br/>"
        f"/api/v1.0/<start> - Min, Max, Avg temp of start date<br/>"
        f"/api/v1.0/<start>/<end> - range of Min, Max, Avg temp of start date"
    )
    
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # query to retrieve the last 12 months of precipitation data and plot the results. 
    last_12_of_rain = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_12_of_rain_str = last_12_of_rain[0]
    oneyear_from_last_date = dt.datetime.strptime(last_12_of_rain_str, "%Y-%m-%d") - dt.timedelta(days=365)
    precp_and_date = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= oneyear_from_last_date).all()
    
    
    precipitation_dict = {}
    for date, prcp in precp_and_date:
        precipitation_dict[date] = prcp

    
    session.close()

    # Convert list of tuples into normal list
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    station_station = session.query(Station.station).all()

    session.close()

    stations_list = []
    for station in station_station:
        stations_list.append(station[0])
            
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    
    last_12_of_rain = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_12_of_rain_str = last_12_of_rain[0]
    oneyear_from_last_date = dt.datetime.strptime(last_12_of_rain_str, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query temperature observations for the most active station over the last year
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_stations_id = most_active_stations[0][0]
    last_12_of_tobs = session.query(Measurement.station, Measurement.tobs).\
    filter(Measurement.station == most_active_stations_id).\
        filter(Measurement.date >= oneyear_from_last_date).all()
    
    session.close()

    tobs_list = []
    for date, tobs in last_12_of_tobs:
        tobs_list.append({"date":date,"temperature":tobs})
    
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=None):
    session = Session(engine)
    
    if end:
        # Start and end date are provided
        station_stats = session.query(func.min(Measurement.tobs),
                              func.max(Measurement.tobs),
                              func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    else:
        # Only start date is provided
        station_stats = session.query(func.min(Measurement.tobs),
                              func.max(Measurement.tobs),
                              func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()



    
    temp_summary = {
        "TMIN": station_stats[0][0],
        "TMAX": station_stats[0][1],
        "TAVG": station_stats[0][2]
    }
    session.close()
    
    return jsonify(temp_summary)



if __name__ == '__main__':
    app.run(debug=True)
