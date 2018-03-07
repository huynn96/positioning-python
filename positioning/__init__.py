from flask import Flask
import MySQLdb

# local imports
from config import app_config


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db = MySQLdb.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DATABASE']
    )

    @app.route('/', methods=['GET'])
    def hello_world():
        curs = db.cursor()
        try:
            curs.execute("SELECT * FROM accelerations LIMIT 10")
            response = curs.fetchall()
            print response
            for row in response:
    			print row
        except:
            print "Error: unable to fetch items"
        return "asd"

    return app
