from flask import Blueprint, current_app, jsonify, request
from .models import Flight, FindFlightsJob
from .database import db
from .kiwi_api import get_flight_prices_for_specific_date
from .find_flights import map_flight_data
bp = Blueprint('api', __name__)


@bp.route('/flights/<int:id>', methods=['GET'])
def get_flight(id):
    flight = Flight.query.filter_by(id=id).first()
    current_app.logger.info(flight.serialize)
    return jsonify({'flight': flight.serialize})


@bp.route('/flights', methods=['GET'])
def get_flights():
    flights = Flight.query.all()
    return jsonify({'flights': [flight.serialize for flight in flights]})


@bp.route('/flights', methods=['POST'])
def create_flight():
    new_flight_parameters = request.get_json()
    # flights = get_flight_prices_for_specific_date('london_gb', 'barcelona_es', '04/06/2019', True)
    current_app.logger.info(new_flight_parameters)
    # flight = map_flight_data(flights[0])
    # current_app.logger.info(flight)
    new_flight = Flight(**new_flight_parameters)
    db.session.add(new_flight)
    db.session.commit()
    return jsonify({'flight': new_flight.serialize})


@bp.route('/flights/<int:id>', methods=['PUT', 'PATCH'])
def update_flight(id):
    update_parameters = request.get_json()
    current_app.logger.info(update_parameters)
    flight = Flight.query.filter_by(id=id).first()
    for param_name, param_value in update_parameters:
        flight[param_name] = param_value
    db.session.commi()
    return jsonify({'route': flight.serialize})


@bp.route('/flights/<int:id>', methods=['DELETE'])
def delete_flight(id):
    flight = Flight.query.filter_by(id=id).first()
    db.session.delete(flight)
    db.session.commit()
    return jsonify({'result': 'deleted flight'})


@bp.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = FindFlightsJob.query.all()
    return jsonify({'jobs': [job.serialize for job in jobs]})


@bp.route('/jobs/<int:id>', methods=['GET'])
def get_job(id):
    job = FindFlightsJob.query.filter_by(id=id).first()
    current_app.logger.info(job.serialize)
    return jsonify({'job': job.serialize})


@bp.route('/jobs', methods=['POST'])
def create_job():
    new_job_parameters = request.get_json()
    current_app.logger.info(new_job_parameters)
    new_job = FindFlightsJob(**new_job_parameters)
    db.session.add(new_job)
    db.session.commit()
    return jsonify({'job': new_job.serialize})


@bp.route('/jobs/<int:id>', methods=['PUT', 'PATCH'])
def update_job(id):
    update_parameters = request.get_json()
    current_app.logger.info(update_parameters)
    job = FindFlightsJob.query.filter_by(id=id).first()
    for param_name, param_value in update_parameters:
        job[param_name] = param_value
    db.session.commi()
    return jsonify({'job': job.serialize})


@bp.route('/jobs/<int:id>', methods=['DELETE'])
def delete_job(id):
    job = FindFlightsJob.query.filter_by(id=id).first()
    db.session.delete(job)
    db.session.commit()
    return jsonify({'result': 'deleted'})


@bp.route('/crons', methods=['GET'])
def get_crons():
    return jsonify({'route': 'get crons'})


@bp.route('/crons/<int:id>', methods=['GET'])
def get_cron(id):
    return jsonify({'route': 'get cron'})


@bp.route('/crons', methods=['POST'])
def create_cron():
    return jsonify({'route': 'create cron'})


@bp.route('/crons/<int:id>', methods=['PUT', 'PATCH'])
def update_cron(id):
    return jsonify({'route': 'update cron'})


@bp.route('/crons/<int:id>', methods=['DELETE'])
def delete_cron(id):
    return jsonify({'route': 'delete cron'})


@bp.route('/', methods=['GET'])
def get_users():
    return jsonify({'result': 'okkk'})
