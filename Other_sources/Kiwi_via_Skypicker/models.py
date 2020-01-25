from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric
from .database import db


class Flight(db.Model):

    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True)
    city_from = Column(String(64), index=True)
    city_to = Column(String(64), index=True)
    distance = Column(Numeric)
    airport_from = Column(String(64))
    airport_to = Column(String(64))
    kiwi_flight_id = Column(String(64))
    price = Column(Numeric, index=True)
    departure_time = Column(TIMESTAMP(timezone=True))
    arrival_time = Column(TIMESTAMP(timezone=True))
    flight_number = Column(String(64))
    cabin_class = Column(String(64))
    airline_code = Column(String(64))

    def __repr__(self):
        return '<Flight {0} from {1} to {2}>'.format(self.flight_number, self.city_from, self.city_to)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'city_from': self.city_from,
            'city_to': self.city_to,
            'distance': float(self.distance),
            'airport_from': self.airport_from,
            'airport_to': self.airport_to,
            'kiwi_flight_id': self.kiwi_flight_id,
            'price': float(self.price),
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
            'flight_number': self.flight_number,
            'cabin_class': self.cabin_class,
            'airline_code': self.airline_code
        }


class FindFlightsJob(db.Model):
    __tablename__ = 'find_flights_jobs'
    id = Column(Integer, primary_key=True)
    city_from = Column(String(64), index=True)
    city_to = Column(String(64))
    departure_date = Column(TIMESTAMP(timezone=True))
    status = Column(String(64))


class CronJob(db.Model):
    __tablename__ = 'cron_jobs'
    id = Column(Integer, primary_key=True)
    day_of_week = Column(String(64))
    month = Column(String(64))
    day_of_month = Column(String(64))
    hour = Column(String(64))
    minute = Column(String(64))
