from flask import Flask, render_template, request, Markup
import numpy as np
import pandas as pd
from utils.fertilizer import fertilizer_dic
import requests
import config
import pickle
from PIL import Image


# Loading model

crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))

fertilizer_recommendation_model_path = 'models/Fertilizer_Recommendation.pkl'
fertilizer_recommendation_model = pickle.load(
    open(fertilizer_recommendation_model_path, 'rb'))


def weather_fetch(city_name):
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None






def weather_fetching(city_name):
    api_key = config.api_key
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
    req = requests.get(url)
    data = req.json()

    name = data['name']
    lon = data['coord']['lon']
    lat = data['coord']['lat']

    exclude = "minute,hourly"
    url2 = f'https://api.openweather.map.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid{api_key}'

    req2 = requests.get(url2)
    data2 = req2.json()

    days = []
    nights = []
    descr = []

    for i in data2['daily']:
        
        days.append(round(i['temp']['day'] - 273.15,2))
        
        #Nights
        nights.append(round(i['temp']['night'] - 273.15,2))

        descr.append(i['weather'][0]['main'] + ": " +i['weather'][0]['description'])

    string = f'[ {name} - 8 days forecast]\n'


    for i in range(len(days)):
    
        if i == 0:
            string += f'\nDay {i+1} (Today)\n'
        
        elif i == 1:
            string += f'\nDay {i+1} (Tomorrow)\n'
        
        else:
            string += f'\nDay {i+1}\n'
        
        string += 'Morning:' + str(days[i]) + '°C' + "\n"
        string += 'Night:' + str(nights[i]) + '°C' + "\n"
        string += 'Conditions:' + descr[i] + '\n'
    return string






app = Flask(__name__)

#home

@ app.route('/')
def home():
    title = 'Home'
    return render_template('index.html', title=title)



#crop
@ app.route('/crop-recommend')
def crop_recommend():
    title = 'Crop Recommendation'
    return render_template('crop.html', title=title)

# fertilizer
@ app.route('/fertilizer')
def fertilizer_recommendation():
    title = 'Fertilizer Suggestion'
    return render_template('fertilizer.html', title=title)





@ app.route('/weather')
def weather():
    title = 'weather Suggestion'
    return render_template('weather.html', title=title)



@app.route('/weather-suggestion',methods=['POST'])
def weather_suggestion():
    title = 'weather suggestion'

    if request.method == 'POST':
        city = request.form.get('city')

        if weather_fetching(city)!= None:
            result = weather_fetching(city)
            return render_template('weather_result.html', prediction=result, title=title)
        else:
            return render_template('try_again.html', title=title)








@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    title = 'Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction, title=title)
        else:

            return render_template('try_again.html', title=title)



@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    title = 'Harvestify - Fertilizer Suggestion'

    crop_name = int(request.form['cropname'])
    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['pottasium'])
    # ph = float(request.form['ph'])


    city = request.form.get("city")
    if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity,crop_name]])
            my_prediction = fertilizer_recommendation_model.predict(data)
            final_prediction = my_prediction[0]
            return render_template('fertilizer-result.html', prediction= final_prediction, title=title)




if __name__ == '__main__':
    app.run(debug=False)
