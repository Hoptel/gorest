#!/usr/bin/env python
import extensions
import uuid
from models import Room, RoomType

from flask import request, Blueprint
from routes.route_utilities import table_get, table_update, table_delete

auth = extensions.auth
db = extensions.db
dataResultSuccess = extensions.dataResultSuccess

room_blueprint = Blueprint("room", __name__, url_prefix='/room')


@auth.login_required(1)
@room_blueprint.route('', methods=['GET', 'POST', 'PATCH', 'DELETE'], endpoint="room")
def endpoint_room():
    if (request.method == 'POST'):
        return table_ins()
    elif (request.method == 'GET'):
        return table_get(Room)
    elif (request.method == 'PATCH'):
        return table_update(Room)
    else:
        return table_delete(Room)


def table_ins():
    requestJson = request.get_json(force=True)
    #if ('roomtype' in list(requestJson.keys()) and requestJson['roomtype'] is not None):
        #roomType = RoomType.query.filter_by(id=requestJson['roomtype'])
        #if (roomType is not None):
            #for key in Room.__table__.columns.keys():
                #if (key not in list(requestJson.keys()) and key != "guid"):
                    #requestJson[key] = roomType[key]
    if ('pricechd' not in list(requestJson.keys())):
        requestJson['pricechd'] = requestJson['price']
    item = Room(**requestJson)
    item.guid = item.guid or uuid.uuid4()
    db.session.add(item)
    db.session.commit()
    return dataResultSuccess(item.to_dict(), code=201, spuriousParameters=list(request.args.to_dict().keys()))
