from flask import Flask,jsonify
from flask import render_template,request
import os
import numpy as np
import pandas as pd
import joblib
import sqlite3
import matplotlib.pyplot as plt
from shapely import wkt
import geopandas as gpd
import shapely
from .data import firingtypesd,typeofflatd,conditiond,geo_blnd,geo_krsd,regio3d,heatingtypesd,citiesd




model_path=os.path.join(os.path.dirname(__file__),'model.pkl')
db_path=os.path.join(os.path.dirname(__file__),'database.sqlite3')



model=joblib.load(model_path)



app=Flask(__name__ ,template_folder='templates')
app.app_context().push()




@app.route("/", methods=["GET","POST"])
def home():
    return render_template('home.html')




@app.route("/prediction", methods=["GET","POST"])
def prediction():
    
    if request.method == 'POST':

        servicecharge=request.form.get('servicecharge')
        balcony=request.form.get('balcony')
        picturecount=request.form.get('picturecount')
        pricetrend=request.form.get('pricetrend')
        kitchen=request.form.get('kitchen')
        yearconstructedrange=request.form.get('yearconstructedrange')
        district=request.form.get('district')
        zipcode=request.form.get('zipcode')
        city=request.form.get('city')
        firingtype=request.form.get('firingtype')
        heatingtype=request.form.get('heatingtype')
        fedaral=request.form.get('fedaral')
        condition=request.form.get('condition')
        typeofflat=request.form.get('typeofflat')

        servicecharge_transformed=[abs(np.log(abs(float(servicecharge+'0')) + 0.0001))]
        picturecount_transformed=[abs(np.log(abs(int(picturecount)) + 0.0001))]
        pricetrend_transformed=[abs(np.log(abs(float(pricetrend)) + 0.0001))]
        yearconstructedrange_transformed=[abs(np.log(abs(int(yearconstructedrange)) + 0.0001))]
        zipcode_transformed=[abs(np.log(abs(int(zipcode)) + 0.0001))]

       
        input_list=servicecharge_transformed+[int(balcony)]+picturecount_transformed+pricetrend_transformed+[int(kitchen)]+yearconstructedrange_transformed+[int(district)]+zipcode_transformed+[int(city)]+eval(firingtype)+eval(heatingtype)+eval(fedaral)+eval(condition)+eval(typeofflat)

        predicted_value=model.predict([input_list])

        transformed_prediction=(np.exp(abs(predicted_value)) - 0.0001)

        return render_template('result.html',predicted_value=round(transformed_prediction[0],2))


    return render_template('prediction.html',districts=geo_krsd,cities=regio3d,firingtypes=firingtypesd,heatingtypes=heatingtypesd,federals=geo_blnd,conditions=conditiond,typeofflat=typeofflatd)




@app.route("/region_rent", methods=["GET","POST"])
def region_rent():

    if request.method == 'POST':
        print("recieved post")

        city=request.form.get('city')

        conn1=sqlite3.connect(db_path)
        conn2=sqlite3.connect(db_path)
        cursor1=conn1.cursor()
        cursor2=conn2.cursor()

        cursor1.execute('SELECT * from df_table')
        cursor2.execute('SELECT * from shape_table')
        df_data = cursor1.fetchall()
        shape_data = cursor2.fetchall()

        data_columns = [column[0] for column in cursor1.description]
        shape_columns = [column[0] for column in cursor2.description]

        data = pd.DataFrame(df_data, columns=data_columns)
        shape = pd.DataFrame(shape_data, columns=shape_columns)

        shape['geometry'] = shape['geometry'].apply(wkt.loads)
        shape['geometry'] = shape['geometry'].apply(lambda x: shapely.geometry.shape(x))
        shape = gpd.GeoDataFrame(shape, geometry='geometry')
       

        cursor1.close()
        cursor2.close()
        conn1.close()
        conn2.close()

        maap = shape[shape['note'].str.endswith(city)]
        
        total_rent_avg_by_plz = data.groupby('geo_plz')['totalRent'].mean().reset_index()

        total_rent_avg_by_plz['geo_plz']=total_rent_avg_by_plz['geo_plz'].astype(int)
        maap['plz']=maap['plz'].astype(int)
        
        gdat_total_rent_avg_by_plz = maap.merge(total_rent_avg_by_plz, left_on="plz", right_on="geo_plz")

        fig, ax = plt.subplots(figsize=(25, 17), facecolor='#474747')
        gdat_total_rent_avg_by_plz.plot(column='totalRent', cmap='Greens', legend=True,ax=ax)
        

        # add text of plz on the map
        for x, y, label in zip(gdat_total_rent_avg_by_plz.geometry.centroid.x, 
                        gdat_total_rent_avg_by_plz.geometry.centroid.y, 
                        gdat_total_rent_avg_by_plz['plz']):
                plt.annotate(label, xy=(x-.01, y), xytext=(2, 2), textcoords="offset points")

        plt.axis('off')
        plt.title(f'Average rent {city} in (€)', fontsize=30, color='white')

        static_folder=os.path.join(app.root_path,'static')
        img_filename=os.path.join(static_folder,'graph.png')

        plt.savefig(img_filename)
        
        return jsonify({'message':'success'})

    return render_template('region_rent.html',cities=citiesd)
    





@app.route("/region_count", methods=["GET","POST"])
def region_count():

    if request.method == 'POST':
        print("recieved post")
        city=request.form.get('city')
        

        conn1=sqlite3.connect(db_path)
        conn2=sqlite3.connect(db_path)
        cursor1=conn1.cursor()
        cursor2=conn2.cursor()

        cursor1.execute('SELECT * from df_table')
        cursor2.execute('SELECT * from shape_table')
        df_data = cursor1.fetchall()
        shape_data = cursor2.fetchall()

        data_columns = [column[0] for column in cursor1.description]
        shape_columns = [column[0] for column in cursor2.description]

        data = pd.DataFrame(df_data, columns=data_columns)
        shape = pd.DataFrame(shape_data, columns=shape_columns)

        shape['geometry'] = shape['geometry'].apply(wkt.loads)
        shape['geometry'] = shape['geometry'].apply(lambda x: shapely.geometry.shape(x))
        shape = gpd.GeoDataFrame(shape, geometry='geometry')
       

        cursor1.close()
        cursor2.close()
        conn1.close()
        conn2.close()

        maap = shape[shape['note'].str.endswith(city)]
        
        offers_by_plz = data.groupby('geo_plz')['totalRent'].count().reset_index()
        offers_by_plz['geo_plz']=offers_by_plz['geo_plz'].astype(int)
        maap['plz']=maap['plz'].astype(int)


        offers_by_plz = maap.merge(offers_by_plz, left_on="plz", right_on="geo_plz")

        fig, ax = plt.subplots(figsize=(25, 17), facecolor='#474747')
        offers_by_plz.plot(column='totalRent', cmap='PuBu', legend=True,ax=ax)

        # add text of plz on the map
        for x, y, label in zip(offers_by_plz.geometry.centroid.x, 
                        offers_by_plz.geometry.centroid.y, 
                        offers_by_plz['plz']):
                plt.annotate(label, xy=(x-.01, y), xytext=(2, 2), textcoords="offset points")

        
        plt.axis('off')
        plt.title(f'Number of rent offers in {city}', fontsize=30)


        static_folder=os.path.join(app.root_path,'static')
        img_filename=os.path.join(static_folder,'graph1.png')

        plt.savefig(img_filename)

        return jsonify({'message':'success'})

    return render_template('region_count.html',cities=citiesd)