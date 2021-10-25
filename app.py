# Imports

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create engine

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

 # Reflect existing database to new model

Base = automap_base()

# Reflect the tables

Base.prepare(engine, reflect=True)


# Save references

Measurements = Base.classes.measurement
Stations = Base.classes.station

 # Create our session from Python to the database

session = Session(engine)

# Flask Setup

app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/temp/start/end"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

# Retrieving precipitation data

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data from the previous year."""

    # Calculating date one year from the last date in dataset

    year_previous = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform query to get the date and precipitation from the previous year

    precipitation = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= year_previous).all()

    session.close()

    # create dictionoary with date as the key and prcp as the value

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# Recieving station data

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Stations.station).all()

    session.close()

    # Turn results into array and convert into a list

    stations = list(np.ravel(results))
    return jsonify(stations=stations)


# Recieving temperature observations

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations for previous year."""

    # Calculating date one year from the last date in dataset

    year_previous = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the main station for all tobs (temperature observations) from the previous year
 
    results = session.query(Measurements.tobs).\
        filter(Measurements.station == 'USC00519281').\
        filter(Measurements.date >= year_previous).all()

    session.close()

    # Turn results into array and convert into a list

    temps = list(np.ravel(results))

    # Return the results

    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""


    sel = [func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]

    if not end:

        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurements.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop points

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurements.date >= start).\
        filter(Measurements.date <= end).all()

    session.close()

    # Turn results into array and convert into a list

    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()


    
