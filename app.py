from flask import Flask, request, render_template, make_response
import folium
import geopandas as gpd
import json
import pandas as pd
import numpy as np
import os
import subprocess
data = gpd.read_file(r'Grunnkretser2020.shp')
data = data.to_crs(epsg=4326)
data['place']=0
for i in range(len(data)):
    if data['grunnkrets'][i][:4]=='0301':
        data['place'][i]=1
data = data[data['place']==1]
data.reset_index(inplace=True)
gk = pd.read_csv(r'529.csv',sep=';',encoding = 'unicode_escape')
data['gk']='0'; data['gkname']='0'
for i in range(len(data)):
    data['gk'][i] = gk['sourceCode'][np.where(gk['targetCode']==int(data['grunnkrets'][i]))[0][0]]
    data['gkname'][i] = gk['sourceName'][np.where(gk['targetCode']==int(data['grunnkrets'][i]))[0][0]]
datagk = data.loc[np.unique(data['gk'],return_index=True)[1]]
datagk.reset_index(inplace=True)

for i in range(len(datagk)):
    poly = data['geometry'].loc[np.where(data['gk']==datagk['gk'][i])]
    datagk['geometry'][i] = poly.unary_union
	
edu = pd.read_excel(r'edu.xls')
rm=[]
for i in range(len(edu)):
    if edu['Utdanning'][i][0]!='D':
        if edu['Utdanning'][i]=='Sentrum':
            continue
        elif edu['Utdanning'][i]=='Marka':
            continue
        rm.append(i)
edu=edu.drop(rm)
edu=edu.drop([112,114]) #remove duplicates
edu=edu.reset_index(drop=True)
edu['DBD']='0'; edu['lowedu']=0.0
for i in range(len(edu)):
    edu['DBD'][i] = edu['Utdanning'][i][9:]
    edu['lowedu'][i] = ((edu['Grunnskole'][i]+edu['Videregående utdanning'][i]+edu['Uoppgitt eller ingen fullført utdanning'][i])/
                     edu['Utdanningsnivå i alt'][i])
edu['DBD'][96]='Sentrum'; edu['DBD'][97] = 'Marka'
datagk['edu'] = 0.0
for i in range(len(datagk)):
    datagk['edu'][i] = edu['lowedu'][np.where(edu['DBD']==datagk['gkname'][i])[0][0]]
	
emp = pd.read_excel(r'emp.xls')
rm=[]
for i in range(len(emp)):
    if emp['Oslo i alt'][i][0]!='D':
        if emp['Oslo i alt'][i]=='Sentrum':
            continue
        elif emp['Oslo i alt'][i]=='Marka':
            continue
        rm.append(i)
emp=emp.drop(rm)
# # dis=dis.drop([112,114]) #remove duplicates
emp=emp.reset_index(drop=True)
emp['DBD']='0'
for i in range(len(emp)):
    emp['DBD'][i] = emp['Oslo i alt'][i][9:]
emp['DBD'][100]='Sentrum'; emp['DBD'][101] = 'Marka'
datagk['emp'] = 0.0
for i in range(len(datagk)):
    datagk['emp'][i] = 100-emp[emp.keys()[2]][np.where(emp['DBD']==datagk['gkname'][i])[0][0]]
	
dis=pd.read_excel(r'dis.xls')
rm=[]
for i in range(len(dis)):
    if dis['Oslo i alt'][i][0]!='D':
        if dis['Oslo i alt'][i]=='Sentrum':
            continue
        elif dis['Oslo i alt'][i]=='Marka':
            continue
        rm.append(i)
dis=dis.drop(rm)
# dis=dis.drop([112,114]) #remove duplicates
dis=dis.reset_index(drop=True)
dis['DBD']='0'
for i in range(len(dis)):
    dis['DBD'][i] = dis['Oslo i alt'][i][9:]
dis['DBD'][100]='Sentrum'; dis['DBD'][101] = 'Marka'
datagk['dis'] = 0.0
for i in range(len(datagk)):
    datagk['dis'][i] = dis[dis.keys()[1]][np.where(dis['DBD']==datagk['gkname'][i])[0][0]]
	
inc=pd.read_excel(r'inc.xls')
rm=[]
for i in range(len(inc)):
    if inc['Oslo i alt'][i][0]!='D':
        if inc['Oslo i alt'][i]=='Sentrum':
            continue
        elif inc['Oslo i alt'][i]=='Marka':
            continue
        rm.append(i)
inc=inc.drop(rm)
inc=inc.drop([117,119]) #remove duplicates
inc=inc.reset_index(drop=True)
inc['DBD']='0'
for i in range(len(inc)):
    inc['DBD'][i] = inc['Oslo i alt'][i][9:]
inc['DBD'][100]='Sentrum'; inc['DBD'][101] = 'Marka'
datagk['inc'] = 0.0
for i in range(len(datagk)):
    datagk['inc'][i] = inc[inc.keys()[1]][np.where(inc['DBD']==datagk['gkname'][i])[0][0]]
	
app = Flask(__name__)

first_time=True

@app.route('/', methods = ['GET','POST'])
def index():
    m = folium.Map(location=[59.95,10.75],zoom_start=10.4)
    #folium.GeoJson(data=datagk['geometry']).add_to(m)    
    #folium.GeoJson(data=data['geometry']).add_to(m)
    
    if request.method=='POST':
        #user_input = request.form['user_input']
        user_input = list(request.form.listvalues())[0]
        print(user_input,len(user_input))
        #print(list(request.form.listvalues())[0])
        m = folium.Map(location=[59.95,10.75],zoom_start=10.4)
        #user_input = request.get_json()
        if len(user_input)==1:
            if user_input[0] == 'Unemployed':
                folium.Choropleth(
                    geo_data=datagk['geometry'],
                    name="choropleth",
                    data=datagk['emp'],
                    columns=["DBD", "emp"],
                    key_on="feature.id",
                    fill_color="Reds",
                    fill_opacity=0.6,
                    line_opacity=0.2,
                    legend_name="Unemployment Rate (%)").add_to(m)
            elif user_input[0] == 'Percentage of persons with at most VGS':
                folium.Choropleth(
                    geo_data=datagk['geometry'],
                    name="choropleth",
                    data=datagk['edu'],
                    columns=["DBD", "edu"],
                    key_on="feature.id",
                    fill_color="Reds",
                    fill_opacity=0.6,
                    line_opacity=0.2,
                    legend_name="Percentage low-education").add_to(m)
            elif user_input[0] == 'Percentage registered disabled':
                folium.Choropleth(
                    geo_data=datagk['geometry'],
                    name="choropleth",
                    data=datagk['dis'],
                    columns=["DBD", "dis"],
                    key_on="feature.id",
                    fill_color="Reds",
                    fill_opacity=0.6,
                    line_opacity=0.2,
                    legend_name="Percentage registered disabled").add_to(m)
            elif user_input[0] == 'Percentage low income households':
                folium.Choropleth(
                    geo_data=datagk['geometry'],
                    name="choropleth",
                    data=datagk['inc'],
                    columns=["DBD", "inc"],
                    key_on="feature.id",
                    fill_color="Reds",
                    fill_opacity=0.6,
                    line_opacity=0.2,
                    legend_name="Percentage low income households").add_to(m)
        elif len(user_input)>1:
            labels = ['Unemployed','Percentage of persons with at most VGS','Percentage registered disabled','Percentage low income households']
            lab_idx = ['emp','edu','dis','inc']
            datagk['new'] = 0.0
            legend = ''
            for i in range(len(labels)):
                if labels[i] in user_input:
                    datagk['new'] = datagk['new']+datagk[lab_idx[i]]
                    legend = legend + str(labels[i])+" | "
            datagk['new'] = datagk['new']/len(user_input)
            folium.Choropleth(
                geo_data=datagk['geometry'],
                name="choropleth",
                data=datagk['new'],
                columns=["DBD", "new"],
                key_on="feature.id",
                fill_color="Reds",
                fill_opacity=0.6,
                line_opacity=0.2,
                legend_name=legend).add_to(m)
        else:
            folium.GeoJson(data=datagk['geometry']).add_to(m)
            
        
    else:
        folium.GeoJson(data=datagk['geometry']).add_to(m)
        
    m.save('templates/map.html')
    subprocess.call(["git", "add", "templates/map.html"])
	  subprocess.call(["git","commit","-m","Update map.html"])
	  subprocess.call(["git","push","origin","master"])
	  map_url = "https://raw.githubusercontent.com/conorak/oslomap/master/templates/map.html"
	  return render_template("index.html",map=map_url)
	#return render_template("index.html",map=m)

if __name__ == '__main__':
    app.run()
