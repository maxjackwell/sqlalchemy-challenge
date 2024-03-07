# Import the dependencies.
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
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
def homepage():
    return(
        f"Welcome to the Maxwell Instituion of Climate Research<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date/start<br/>"
        f"/api/v1.0/date/start/end<br/>"
        f"Hint: When using dates, use the MMDDYYYY formula<br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_data = session.query(Measurement).order_by(Measurement.date.desc()).first()
    recent_data.date
    recent_date = dt.datetime.strptime(recent_data.date, '%Y-%m-%d').date()
    year_ago = recent_date - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()
    # Convert the query results from your precipitation analysis 
    # (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    precip_dict = {}
    for result in precip_data:
        date = result.date
        prcp = result.prcp
        precip_dict[date] = prcp

    # Return the JSON representation of your dictionary.
        return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    station_results = session.query(Station.station).all()
    station_list = [result[0] for result in station_results]
    
    # Return the JSON list of stations
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    year_ago2 = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= year_ago2).all()
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    tobs_list = []
    for result in temp_data:
        date = result.date
        tobs = result.tobs
        tobs_list.append(tobs)
    # Return a JSON list of temperature observations for the previous year.
    return jsonify(tobs_list)


@app.route("/api/v1.0/date/<start>")
@app.route("/api/v1.0/date/<start>/<end>")
def stats(start=None, end=None):
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature
    # for a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    
    start_date = dt.datetime.strptime(start, "%m%d%Y")
    temp = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    
    if not end:
        results = session.query(*temp).filter(Measurement.date >= start_date).all()
    else:
        end_date = dt.datetime.strptime(end, "%m%d%Y")
        results = session.query(*temp).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug=True)