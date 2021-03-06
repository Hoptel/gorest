#!/usr/bin/env python
import extensions
from models import Room, Reservation
from flask import request, Blueprint
from datetime import timedelta
from sqlalchemy import and_

auth = extensions.auth
db = extensions.db
dataResultSuccess = extensions.dataResultSuccess
stringToDateTime = extensions.stringToDateTime

reservat_blueprint = Blueprint("reservat", __name__, url_prefix='/reservat')


@auth.login_required(1)
@reservat_blueprint.route('/forecast/day', methods=['GET'], endpoint='forecast_day')
def forecastDay():
    args = request.args.to_dict()
    startDate = stringToDateTime(args.pop('startdate'))
    endDate = stringToDateTime(args.pop('enddate'))
    timecount = startDate
    returnData = []

    while timecount <= endDate:
        returnData.append(generateForecastDayData(timecount))
        timecount += timedelta(days=1)

    return dataResultSuccess(returnData, spuriousParameters=args, count=len(returnData))


def generateForecastDayData(date):
    returnData = dict()

    roomCount = Room.query.count()
    roomOcc = Reservation.query.filter(and_(Reservation.startdate <= date, Reservation.enddate >= date)).count()

    returnData['aday'] = date.day
    returnData['amonth'] = date.month
    returnData['ayear'] = date.year
    returnData['totalemptyroom'] = roomCount - roomOcc
    returnData['totalroom'] = roomOcc

    return returnData


@auth.login_required(1)
@reservat_blueprint.route('/forecast/totals', methods=['GET'], endpoint='forecast_totals')
def forecastTotals():
    args = request.args.to_dict()
    startDate = stringToDateTime(args.pop('startdate'))
    endDate = stringToDateTime(args.pop('enddate'))

    ciroom = Reservation.query.filter(and_(Reservation.startdate >= startDate, Reservation.startdate <= endDate)).count()
    coroom = Reservation.query.filter(and_(Reservation.enddate >= startDate, Reservation.enddate <= endDate)).count()
    huroom = Reservation.query.filter(and_(Reservation.startdate == Reservation.enddate, Reservation.startdate >= startDate, Reservation.startdate <= endDate)).count()
    totalroom = Room.query.count()
    occrate = 0.0
    if (totalroom > 0):
        occrate = ((ciroom / ((endDate - startDate).days + 1)) / totalroom) * 100
    
    # totaloccbed =

    returnData = {'ciroom': ciroom, 'coroom': coroom, 'huroom': huroom, 'totalroom': totalroom, 'occrate': occrate}
    return dataResultSuccess([returnData], spuriousParameters=args)
