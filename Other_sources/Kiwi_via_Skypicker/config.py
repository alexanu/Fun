import os
# from pathlib import Path
# from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# env_path = Path('../.env')
# load_dotenv(dotenv_path=env_path)

class BaseConfig(object):
    SECRET_KEY = 'secret'
    DEBUG = True
    DB_NAME = 'flight-prices'
    DB_USER = 'flight-prices'
    DB_PASS = 'flight-prices-pass'
    DB_SERVICE = 'postgres'
    DB_PORT = '5432'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
