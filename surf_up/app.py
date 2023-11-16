                    # Import the dependencies.
import numpy as np
import sqlalchemy
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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
        
    )
  #precipitation route  
@app.route("/api/v1.0/precipitation")
def precipitation():
   session = Session(engine)
   query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)   

   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter( Measurement.date >= query_date ).all()
   session.close()
   precipitation_data = {date: prcp for date, prcp in precipitation}
   return jsonify(precipitation_data)

 # stations route
@app.route("/api/v1.0/stations")
def stations():
   session = Session(engine)
   
   stations = session.query(func.distinct(Measurement.station)).all()
   station_ids = [station[0] for station in stations]
   session.close()
   return jsonify(station_ids)

#tobs route
@app.route("/api/v1.0/tobs")
def tobs():
   session = Session(engine)
   query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365) 
   most_active_station_id = session.query(
                    Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
   tewlve_month_temp = session.query(Measurement.date, Measurement.tobs).\
    filter( Measurement.date >= query_date).\
    filter( Measurement.station == most_active_station_id ).all()
   tewlve_month_temp_data = {date: tobs for date, tobs in tewlve_month_temp}

   session.close()
   return jsonify(tewlve_month_temp_data)

# start route
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    calculation = session.query(
    func.min(Measurement.tobs).label('min_temp'),
    func.max(Measurement.tobs).label('max_temp'),
    func.avg(Measurement.tobs).label('avg_temp')
    ).\
    filter( Measurement.date == start).all()
    calculation_data = []
    for min_temp, max_temp, avg_temp in calculation:
        calculation_dict = {}
        calculation_dict["min_temp"] = min_temp
        calculation_dict["max_temp"] = max_temp
        calculation_dict["avg_temp"] = avg_temp
        calculation_data.append(calculation_dict)
    session.close()    

    return jsonify(calculation_data)

# start/End route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    session = Session(engine)
    calc = session.query(
    func.min(Measurement.tobs).label('min_temp'),
    func.max(Measurement.tobs).label('max_temp'),
    func.avg(Measurement.tobs).label('avg_temp')
    ).\
    filter((Measurement.date.between(start, end))).all()
    calc_data = []
    for min_temp, max_temp, avg_temp in calc:
        calc_dict = {}
        calc_dict["min_temp"] = min_temp
        calc_dict["max_temp"] = max_temp
        calc_dict["avg_temp"] = avg_temp
        calc_data.append(calc_dict)
    session.close()    

    return jsonify(calc_data)


    


if __name__ == '__main__':
    app.run(debug=True)