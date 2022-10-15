#authhor:kalpaG 2022/09/30
#!/usr/bin/env python3
import csv
import urllib 
import http.cookiejar as cookielib  ## http.cookiejar in python3
import mechanize
from bs4 import BeautifulSoup
import pandas as pd 
from datetime import datetime, timedelta
from dateutil.parser import parse

def CleanupString(string):
    return "".join(string.replace('\n','').strip().split())

baseurl = "https://ouhagm.medirota.com"
email = 'vingifernando@gmail.com'
password = '@Kurulu14314'
loginurl = baseurl + "/login/"

#this date should be in YYYY-MM-DD format and ideally should be monday 
roster_start_date='2022-10-03'
number_of_weeks_ahead=46 #roster will be retrieved for this many weeks
cj = cookielib.CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
 #login
br.open(loginurl)
br.select_form(nr=0)
br.form['t_email'] = email
br.form['t_password'] = password
br.submit()

masterdic={}
    
for weekno in range(number_of_weeks_ahead):
    weekstart = str((parse(roster_start_date) + timedelta(weeks=weekno)).strftime('%Y-%m-%d'))
    print(str(weekno+1)+":  processing the week starting from = " +weekstart)
    rosterlink = baseurl + "/rota/" + weekstart + "/people/?entity_filter=person-1802&rotamap_show=True&empty_rota_rows_show=false"
    weeklydic={}
    dayslist=[]
    for day in range(7):
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
    
    masterdic[str(weekno)]=weeklydic

with open('Roster_Vihangi.csv', 'w') as f:
    for i in masterdic:
        weekdic =  masterdic[i].items()  
        for x,y in weekdic:
            f.write("%s,%s\n"%(y, x))
            
            

            