import numpy as np
import pandas as pd 
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# import flask
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn=engine.connect()

# reflect an existing database into a new model
Base= automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)
# Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# change
# Create our session (link) from Python to the DB
session=Session(engine)
print('test')
# Create an app
app=Flask(__name__)

# Flask Routes
@app.route("/api/v1.0/")
def welcome():
# List all available api routes.
    return(
        f"Welcome to the Hawaii Climate home page. Let's find the tempature for your vacation.<br/>"
        f"Available Routes:<br/><br/>"

        f"List of prior year rain totals from all stations.<br/>"
        f"/api/v1.0/precipitation<br/><br/>"

        f"List of all stations.<br/>"
        f"/api/v1.0/stations<br/><br/>"

        f"List of Tempature Observations (TOBS) for the previous year from the most active station.<br/>"
        f"/api/v1.0/tobs<br/><br/>"

        f"When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date.<br/>" 
        f"/api/v1.0/<start> (enter date format as: yyyy-mm-dd)<br/><br/>"

        f"When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date.<br/>"  
        f"/api/v1.0/<start>/<end> (enter date format as: yyyy-mm-dd/yyyy-mm-dd)<br/>"
      
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # """Return a list of rain fall for prior year"""
#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the JSON representation of your dictionary.
# Calculate the date 1 year ago from the last data point in the database
#last_data_point is ('2017 -08-23')
    session=Session(engine)
    last_data_point=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
# last_data_point

# datetime.date(2016, 8, 23)
    year_ago=dt.date(2017, 8, 23)-dt.timedelta(days=365)
# year_ago

# Perform a query to retrieve the date and precipitation scores
    rain=session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>year_ago).\
        order_by(Measurement.date).all()
   
    session.close()    

# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals=[]
    for result in rain:
        row={}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)

    return jsonify(rain_totals)    


@app.route("/api/v1.0/stations")
def stations():  
#   Return a JSON list of stations from the dataset
    session=Session(engine)

    results=session.query(Station.station).\
        group_by(Station.station).all()
    results    
    return jsonify(results)
    session.close()
    


@app.route("/api/v1.0/tobs")
def tobs():    
#     Return a list of temperatures for prior year
#    * Query for the dates and temperature observations OF THE MOST ACTIVE STATION from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#           * Return the JSON observation (TOBS) FOR THE PREVIOUS YEAR
    session=Session(engine)

    prev_year=dt.date(2017, 8, 23)-dt.timedelta(days=365)

    temp=session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= prev_year).\
        filter(Measurement.station =='USC00519281').\
        order_by(Measurement. date).all()

    temp_totals=[]
    for results in temp:
        row={}
        row["date"]=temp[0]    
        row["tobs"]=temp[1]
        temp_totals.append(row)
        
    return jsonify(temp_totals)    

    session.close()

@app.route("/api/v1.0/<start>")
def start(start=None):
#         Return a list of temperatures for prior year
#    *Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#       *When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#       *When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    session=Session(engine)
    # start_date=dt.date(2017,8,2)
    # end_date=dt.date(2017,8,23)

    trip_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    # trip=list(np.ravel(trip_data))

    session.close()

    stattemps = []
    for result in trip_data:
        stats = {}
        stats['Date'] = start
        stats['Min Temperature'] = result[1]
        stats['Avg Temperature'] = result[2]
        stats['Max Temperature'] = result[3]
        stattemps.append(stats)
    #print results as JSON
    return jsonify(stattemps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    #create session
    session = Session(engine)
    #query to find the temp min, avg, and max at a given start-end range
    trip_data2 = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()    
    session.close()

    #create list in dict format
    stattemps2 = []
    for result in trip_data2:
        stats2 = {}
        stats2['Start Date'] = start
        stats2['End Date'] = end
        stats2['Min Temperature'] = result[1]
        stats2['Avg Temperature'] = result[2]
        stats2['Max Temperature'] = result[3]
        stattemps2.append(stats2)
    #print results as JSON
    return jsonify(stattemps2)



#Define main behavior 
if __name__ == "__main__":
    app.run(debug=True)