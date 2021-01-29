# app.py
import logging
import os
import requests
import pkg_resources

from flask import Flask, request, jsonify, abort, render_template, url_for, Blueprint

from oscar_schedules import Schedule , number_expected, getSchedules
#from oscar_views import getMonitoring

from datetime import timedelta, datetime

app = Flask(__name__ , static_folder="static", template_folder="templates" )


if "PROXY_URL" in os.environ:
    from flask_reverse_proxy_fix.middleware import ReverseProxyPrefixFix
    app.config['REVERSE_PROXY_PATH'] = os.environ.get('PROXY_URL')
    ReverseProxyPrefixFix(app)

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
version = pkg_resources.get_distribution('oscar-schedules').version

variables_map = {
    224 : "Air temperature",
    216 : "Atmospheric pressure",
    251 : "Humidity",
    309 : "Wind",
    210 : "Precipitation",
    12005 : "Horizontal wind direction",
    12006 : "Horizontal wind speed",
    227 : "Temperature profile",
    12000 : "Atmospheric pressure profile",
    310 : "Upper wind",
    256 : "Watervapor profile"
    
}

#@app.route('/views/jenny')
#def monitoring():
#    def generate():
#        for region in ["africa","antarctica","asia","europe","northCentralAmericaCaribbean","southAmerica","southWestPacific"]:
#            yield getMonitoring(region) + '\n'
#    return Response(generate(), mimetype='text/csv')

@app.route('/propose_wigosid')
def proposewigosid():
    term = request.args.get("term", None)
    
    r = requests.get("https://oscar.wmo.int/surface/rest/api/stations/approvedStations/wigosIds?pageSize=100&q={}&page=1".format(term)).json()
    
    wigos_ids = []
    if r["total"] > 0 :
        wigos_ids = [ e["text"] for e in r["resultList"] ]
    
    return jsonify( wigos_ids )

@app.route('/')
def oscar_schedules():
    return render_template('index.html', variables= [ {'id':id , 'name':name} for id,name in variables_map.items() ] , version = version )


@app.route('/number_expected/<string:wigos_id>', methods=['GET'])
def nr_expected(wigos_id):
    period = request.args.get("date", None)
    variables = request.args.get("variables", None)
    

    if not len(wigos_id.split("-"))==4:
        abort(400,"wigos id {} not in right format".format(wigos_id))

    if not period:
        abort(400,"need to supply period parameter")
    
    try:
        period = datetime.strptime(period,"%Y-%m-%d")
    except:
        abort(400,"date format error")

    variables = variables.split(',') if variables else []
    logger.info("variables {}".format(variables))    
    try:
        variables = list(variables_map.keys()) if 'ALL' in variables else [ int(v) for v in variables ]
    except:
        abort(400,"variables need to be specified as intergers")
    
    # get schedules 
    mydate = period # the date and hour for which we calculate the number of expected

    # +- 3h interval around the date
    lower_boundary = mydate - timedelta(hours=3) 
    upper_boundary = mydate + timedelta(hours=3)

    logger.info("checking number expected for station {} and variables {} interval {} to {}".format(wigos_id,variables,lower_boundary,upper_boundary))

    

    infos = getSchedules(wigos_id,  variables )
    observations = infos["observations"]
    name = infos["name"]

    response = { "wigos_id" : wigos_id , "name" : name , "variables" : [] }

    for var_id,info in observations.items():
        schedules = info["schedules"]
        name = info["variableName"]
        
        if len(schedules) == 0:
            continue
        
        e = {}
        for sh in [0,6,12,18]:
            e["h{}".format(sh)] = number_expected(schedules,lower_boundary + timedelta(hours=sh) ,upper_boundary + timedelta(hours=sh))
        
        response["variables"].append( {  'var_id' : var_id , 'variable' : name , 'nr_expected' : e , 'schedules' : [ str(s) for s in schedules] } )
        
        #print("variable: {} expected: {} for schedules {}".format(var_mapping[var_id],e,  ",".join([ str(s) for s in schedules ])  ))

    # Return the response in json format
    return jsonify(response)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, host="0.0.0.0", port=5000)