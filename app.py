import datetime as dt
import selectors
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)
app = Flask(__name__)

@app.route('/')
def welcome():
    return (
        f'This is the Hawaii Climate Analysis API!<br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/start/YYYY-MM-DD<start><br/>'
        f'/api/v1.0/start/YYYY-MM-DD<start>/end/YYYY-MM-DD<end>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    newest_date = (dt.datetime.strptime(session.query(func.max(measurement.date)).first()[0], '%Y-%m-%d')).date()
    last_year = newest_date - dt.timedelta(days=365)

    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= last_year).all()

    session.close()

    precipitate = {}
    for i, j in precipitation:
        precipitate[i] = j
    return jsonify(precipitation=precipitate)



@app.route('/api/v1.0/stations')
def stations():
    results = session.query(station.station).all()

    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route('/api/v1.0/tobs')
def monthly_temp():
    newest_date = (dt.datetime.strptime(session.query(func.max(measurement.date)).first()[0], '%Y-%m-%d')).date()
    last_year = newest_date - dt.timedelta(days=365)

    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= last_year).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)


@app.route('/api/v1.0/start/<start>')
def stats(start):
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()

    session.close()

    start_temp = list(np.ravel(results))
    stats_index = ['Min Temp', 'Max Temp', 'Avg Temp']
    temp_stats = {stats_index[i]: start_temp[i] for i in range(len(stats_index))}

    return jsonify(temp_stats)


@app.route('/api/v1.0/start/<start>/end/<end>')
def end_stats(start, end):
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter((measurement.date >= start) & (measurement.date <= end)).all()
    session.close()

    start_end_temp = list(np.ravel(results))
    stats_index = ['Min Temp', 'Max Temp', 'Avg Temp']
    start_end_temp_stats = {stats_index[i]: start_end_temp[i] for i in range(len(stats_index))}

    return jsonify(start_end_temp_stats)




if __name__ == '__main__':
    app.run()