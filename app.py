

import streamlit as st
import requests
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="Solar Panel Efficiency Calculator ☀️")

st.title("☀️ Solar Panel Efficiency Calculator")
st.markdown("Estimate your solar energy output using real-time weather data.")

# --- Inputs ---
city = st.text_input("Enter your city", "Toronto")
api_key = st.text_input("OpenWeatherMap API Key", type="password")
panel_power = st.number_input("Panel Wattage (W)", min_value=10, max_value=700, value=400)
num_panels = st.number_input("Number of Panels", min_value=1, max_value = 100, value=10)
efficiency = st.slider("Panel Efficiency (%)", 10, 25, 18)

# --- Get Coordinates from City Name ---
def get_coordinates(city, api_key):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    if data:
        return data[0]["lat"], data[0]["lon"]
    else:
        return None, None


 # --- Get Weather Data ---
def get_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

# --- Calculate Energy Output ---
def calculate_output(irradiance, panel_power, num_panels, efficiency, sunlight_hours):
    total_kw = (panel_power * num_panels) / 1000
    output = total_kw * (efficiency / 100) * irradiance
    return output

# --- Main Execution ---
if city and api_key:
    lat, lon = get_coordinates(city, api_key)
    if lat and lon:
        weather_data = get_weather_data(lat, lon, api_key)
        if weather_data:
            # Approximate daily sunlight hours and irradiance from cloud cover
            cloud_cover = weather_data["clouds"]["all"]
            temp = weather_data["main"]["temp"]
            base_irradiance = 5.0  # Average for moderate sunlight
            irradiance = base_irradiance * (1 - cloud_cover / 100)  # simple approximation
            sunlight_hours = 12 * (1 - cloud_cover / 100)

            daily_output = calculate_output(irradiance, panel_power, num_panels, efficiency, sunlight_hours)
            monthly_output = daily_output * 30
            co2_saved = daily_output * 0.92

            # Display results
            st.subheader("Estimated Output")
            st.write(f"**Daily Output:** {daily_output:.2f} kWh/day")
            st.write(f"**Monthly Output:** {monthly_output:.2f} kWh/month")
            st.write(f"**Estimated CO₂ saved/day:** {co2_saved:.2f} kg")

            # Visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(x=["Daily", "Monthly"], y=[daily_output, monthly_output], marker_color='orange'))
            fig.update_layout(title="Solar Energy Output", yaxis_title="kWh")
            st.plotly_chart(fig)
        else:
            st.error("Couldn't fetch weather data.")
    else:
        st.error("Invalid city name.")
else:
    st.info("Enter your city and API key to get started.")

