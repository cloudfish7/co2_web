from bottle import route, run, template, redirect, request
import linecache
import json
from bottle import get, static_file

CO2_DATA_FILE_1M='/opt/co2log/co2data_1m.txt'
CO2_DATA_FILE_1H='/opt/co2log/co2data_1h.txt'
#TAIL_ROW=20
#REFRESH_INTERVAL=2

def get_co2_data(file_name,get_line_num):

    labels = []
    data =[]
    num_lines = sum(1 for line in open(file_name))
    tail_line = get_line_num
    if( num_lines < get_line_num ):
       tail_line = num_lines
    
    for x in range(num_lines - tail_line + 1, num_lines)[::-1]:
      target_line = linecache.getline(file_name, x)
      d = target_line.split(",")
      labels.append(d[0][-8:])
      data.append(d[1])
      #print(target_line)
      linecache.clearcache()
    
    return labels,data

def get_co2_data_past_6h():
    return get_co2_data(CO2_DATA_FILE_1H,6)

def get_co2_data_past_60m():
    return get_co2_data(CO2_DATA_FILE_1M,60)

def get_co2_data_latest():
    return get_co2_data(CO2_DATA_FILE_1M,2)

def create_chart_url(func):
    labels,data = func()    

    graph_config={
        'type' : "line",
        'data':{
            'labels':labels[::-1],
            'datasets':[
                {
                    'label':'CO2',
                    'data':data[::-1]
                }
            ]
        }
    }

    chart_url = "https://quickchart.io/chart?bkg=white&c={}".format(json.dumps(graph_config))

    return chart_url
  
def get_latest_data():
    labels,data = get_co2_data_latest()    
    return labels[0],data[0]

# Static file Routing ------------------------------------------------
#@get("/static/css/<filepath:re:.*\.css>")
@get("/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="static/css")

@get("/static/font/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath):
    return static_file(filepath, root="static/font")

@get("/static/img/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="static/img")

#@get("/static/js/<filepath:re:.*\.js>")
@get("/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

# Dynamic Page ------------------------------------------------------
@route("/")
def index():
   # latest
   latest_time,latest_data = get_latest_data()    
   # Past 60m
   chart_url_60m = create_chart_url(get_co2_data_past_60m)
   # Past 6h
   chart_url_6h = create_chart_url(get_co2_data_past_6h)

   return template("index", chart_url_60m=chart_url_60m,chart_url_6h=chart_url_6h,latest_time=latest_time,latest_data=latest_data)

# Entry Point
run(host='raspberrypico2.local', port=8080, debug=True)
