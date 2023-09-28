from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)

OPENWEATHERMAP_API_KEY = "c4c15053dd686e6fb27ed7509db1f4a8"
TRIPADVISOR_API_KEY = "8D68C83380F04604AD4D4988DA8165E5"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
    try:
        if request.method == 'POST':
            # Get the city name from the form data
            city = request.form.get('city', 'Bali')
        else:
            # If it's a GET request, use the default city as "Bali"
            city = 'Bali'

        # Define the URL for the TripAdvisor API
        tripadvisor_url = f"https://api.content.tripadvisor.com/api/v1/location/search?searchQuery={city}&category=hotels&language=en&key={TRIPADVISOR_API_KEY}"

        # Make a request to the TripAdvisor API
        tripadvisor_response = requests.get(tripadvisor_url, headers={"accept": "application/json"})
        tripadvisor_data = tripadvisor_response.json()

        # Extract the location_id from the TripAdvisor response
        location_id = tripadvisor_data['data'][0]['location_id']

        # Define the URL for getting hotel data based on location_id
        hotels_url = f"https://api.tripadvisor.com/data/1.0/locations/{location_id}/hotels?key={TRIPADVISOR_API_KEY}"

        # Make a request to the TripAdvisor API to get hotel data for the city
        hotels_response = requests.get(hotels_url)
        hotels_data = hotels_response.json()

        # Extract hotel information from the TripAdvisor response
        hotels = hotels_data.get('hotels', [])

        hotel_list = []
        for hotel in hotels:
            location_id = hotel['location_id']
            name = hotel['name']
            address_obj = hotel.get('address_obj', {})
            street1 = address_obj.get('street1', '')
            street2 = address_obj.get('street2', '')
            city = address_obj.get('city', '')
            country = address_obj.get('country', '')
            postalcode = address_obj.get('postalcode', '')
            address_string = address_obj.get('address_string', '')

            hotel_info = {
                'location_id': location_id,
                'name': name,
                'street1': street1,
                'street2': street2,
                'city': city,
                'country': country,
                'postalcode': postalcode,
                'address_string': address_string
            }
            hotel_list.append(hotel_info)

        # Define the URL for the OpenWeatherMap API
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}"

        # Make a request to the OpenWeatherMap API
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        # Extract weather information from the OpenWeatherMap response
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']

        weather_info = {
            'temperature': temperature,
            'humidity': humidity,
            'description': description
        }

        # Combine hotel and weather information into a single response
        response_data = {
            'city': city,
            'hotels': hotel_list,
            'weather': weather_info
        }

        return render_template('result.html', data=response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
