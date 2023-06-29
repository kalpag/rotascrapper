#authhor:kalpaG 2022/09/30
#!/usr/bin/env python3
import csv
from multiprocessing.resource_sharer import stop
import sys
import urllib 
import http.cookiejar as cookielib  ## http.cookiejar in python3
import mechanize
from bs4 import BeautifulSoup
import pandas as pd 
from datetime import datetime, timedelta
from dateutil.parser import parse
import configparser 
import datetime

try :
    configur = configparser.ConfigParser()
    configur.read('Configs.cfg')
    baseurl = configur.get('INFO', 'baseurl')
    email = configur.get('INFO', 'email')
    password = configur.get('INFO', 'password')
    roster_start_date = configur.get('INFO', 'roster_start_date')  #this date should be in YYYY-MM-DD format and should be monday
    
    tdate = datetime.datetime.strptime(roster_start_date, "%Y-%m-%d").date()
    roster_starting_monday = tdate - datetime.timedelta(days=tdate.weekday())
    print("roster starting on Monday : " + str(roster_starting_monday))
     
    
    number_of_weeks_ahead = int(configur.get('INFO', 'number_of_weeks_ahead')) #roster will be retrieved for this many weeks
    person_id = configur.get('INFO', 'personid')
     
except Exception as e :
    print("Config file related error occured : " +str(e))
    sys.exit(1)

def CleanupString(string):
    return "".join(string.replace('\n','').strip().split())

loginurl = baseurl+"/login/"

try :
    cj = cookielib.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)
   
     #login
    br.open(loginurl)
    br.select_form(nr=0)
    br.form['t_email'] = email
    br.form['t_password'] = password
    resp = br.submit()
    if resp.code != 200 :
        print("Login info incorrect ")
        print(str(resp.read()))
        sys.exit(1)
except Exception as e :
    print("Error Occurred while connecting to medirota : " + str(e))
    sys.exit(1)

masterdic={}
    
for weekno in range(number_of_weeks_ahead):
    weekstart = str((roster_starting_monday + timedelta(weeks=weekno)).strftime('%Y-%m-%d'))
    print(str(weekno+1)+":  processing the week starting from = " +weekstart)
    rosterlink = baseurl + "/rota/" + weekstart + "/people/?entity_filter=person-" + person_id + "&rotamap_show=True&empty_rota_rows_show=false"
    weeklydic={}
    dayslist=[]
    for day in range(7): #7 days of the week
        val=(parse(weekstart) + timedelta(days=day)).strftime('%Y-%m-%d')
        dayslist.append(val);         
   
    #retrieve roster 
    br.open(rosterlink)

    #process output
    html = BeautifulSoup(br.response().read(), 'html.parser')
    table = html.find('table', class_='rmap-rota__sessions-table') 
    
    try:
        columns = table.tbody.find_all('tr')[0].find_all('td')
    except:
        continue
    
    try:
        if(columns != []):    
            for i in range(1,8):
                weeklydic[dayslist[i-1]]=  CleanupString(columns[i].find_all('li')[0].text)
                #print("extracting information for date : " + str(dayslist[i-1]))
    except Exception as e:
        print("Error Occurred : " + str(e))
        continue
    
    print(weeklydic)
    masterdic[str(weekno)]=weeklydic

with open('Roster_Vihangi.csv', 'w') as f:
    for i in masterdic:
        weekdic =  masterdic[i].items()  
        for x,y in weekdic:
            f.write("%s,%s\n"%(y, x))
            
            

 