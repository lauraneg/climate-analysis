#dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
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
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def retrieve():
    """Return the precipitation data for the last year"""
# Calculate the date 1 year ago from last date in database
    year_minus_1 = dt.date(2017, 8, 23) - dt.date(2000, 8, 23)+ dt.date(1999, 8, 23)
# Query for the date and precipitation for the last year
    retrieve = session.query(measurement.date, measurement.prcp).filter(measurement.date >=year_minus_1).all()
    session.close()
    
# Dict with date as the key and prcp as the value
    pre = {date: precipitation for date, precipitation in retrieve}
    return jsonify(pre)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(station.station).all()
    session.close()

# Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
# Calculate the date 1 year ago from last date in database
    year_minus_1 = dt.date(2017, 8, 23) - dt.date(2000, 8, 23)+ dt.date(1999, 8, 23)

# Query the primary station for all tobs from the last year
    retrieve = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= year_minus_1).all()

    session.close()
# Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(retrieve))

# Return the results
    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
# Select statement
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        retrieve = session.query(*sel).\
            filter(measurement.date >= start).all()
        session.close()

        temps = list(np.ravel(retrieve))
        return jsonify(temps)

# calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    retrieve = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

# Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(retrieve))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()
