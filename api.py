#!/usr/bin/env python
import threading
import time
import uuid

from flask import Flask
from extensions import db, getCurrenciesFromAPI  # , alembic


currencyThread = None


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'the quick brown dog jumps over the lazy fox'
    # mysql+pymysql://<username>:<password>@<host>/<dbname>'
    # (using sqlite for dev purposes)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['UPLOAD_FOLDER'] = '/storage/dbfile'

    # alembic.init_app(app)
    db.init_app(app)

    import models  # noqa: F401

    with app.app_context():
        db.create_all()
        db.session.commit()
        # alembic.revision('making changes')
        # alembic.upgrade()

    from routes.route_utilities import verify_token  # noqa: F401
    from routes.user import user_blueprint
    from routes.dbfile import dbfile_blueprint
    from routes.auth import auth_blueprint
    from routes.employee import employee_blueprint
    # from routes.cost import cost_blueprint
    from routes.reservation import reservation_blueprint
    from routes.roomtype import roomtype_blueprint
    from routes.room import room_blueprint
    from routes.sale import sale_blueprint
    from routes.reservat import reservat_blueprint
    from routes.statgen import statgen_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(dbfile_blueprint)
    app.register_blueprint(employee_blueprint)
    # app.register_blueprint(cost_blueprint)
    app.register_blueprint(reservation_blueprint)
    app.register_blueprint(roomtype_blueprint)
    app.register_blueprint(room_blueprint)
    app.register_blueprint(sale_blueprint)
    app.register_blueprint(reservat_blueprint)
    app.register_blueprint(statgen_blueprint)


    currencyThread = threading.Thread(target=putCurrenciesInDB, args=(app,))
    # currencyThread.start()  # enable for testing and production only

    return app


def putCurrenciesInDB(app):
    import models
    while(True):
        with app.app_context():
            currDict = getCurrenciesFromAPI()
            for key, value in currDict.items():
                curr = models.Currency.query.filter_by(code=key).first()
                if (curr is None):
                    curr = models.Currency(code=key, value=value, guid=uuid.uuid4())
                    db.session.add(curr)
                else:
                    curr.value = value
            db.session.commit()
        time.sleep(3600)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

currencyThread.join()
