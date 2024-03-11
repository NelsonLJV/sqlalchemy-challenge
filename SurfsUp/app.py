# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect existing database to a new model
Base = automap_base()

# Do the same with tables
Base.prepare(autoload_with=engine)

# Store references for tables
Measurement = Base.classes.measurement
Station = Base.classes.measurement

# Create Session
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

#Route Precipitation First
@app.route("/api/v1.0/precipitation")
def get_precipitation():
    
    # Calculate one year ago the latest date
    recent_dt = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_dt = datetime.strptime(recent_dt, '%Y-%m-%d')
    one_year = most_recent_dt - timedelta(days=365)

    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year).\
    order_by(Measurement.date).all()
    
    # Convert results to a dictionary
    rain_data = {result.date: result.prcp for result in results}

    return jsonify(rain_data)

#Route Stations
@app.route("/api/v1.0/stations")
def get_stations():
    
    # Query stations
    stations = session.query(Measurement.station).\
    group_by(Measurement.station).all()
    
    session.close()

    # Convert list
    stations_data = list(np.ravel(stations))
    return jsonify(stations_data)

#Route tobs
@app.route("/api/v1.0/tobs")
def get_tobs():
    
    # Retrieve the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate one year ago the latest date
    recent_dt = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_dt = datetime.strptime(recent_dt, '%Y-%m-%d')
    one_year = most_recent_dt - timedelta(days=365)
    

    # Query tobs data for above data
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year).all()
    
    session.close()
    
    # Store the data into a dictionary
    tobs_data = [{"date": result.date, "tobs": result.tobs} for result in tobs_results]

    return jsonify(tobs_data)


if __name__ == "__main__":
    app.run(port = 8080)
