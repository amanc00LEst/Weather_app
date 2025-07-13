import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Title
st.set_page_config(page_title="Weather Forecast", layout="wide")

st.markdown(
    """
    <style>
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: -1;
    }
    .main * {
        color: white !important;
        font-weight: 500;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }
    </style>
    <div class="overlay"></div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align: center; font-family: "Trebuchet MS", sans-serif; font-size: 48px; font-weight: 700; color: white;'>
        Weather Forecast App
    </h1>
    """,
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.header("Search Weather")
city = st.sidebar.text_input("Select City")

units = st.sidebar.radio("Units", ["Celsius", "Fahrenheit"])
unit_symbol = "°C" if units == "Celsius" else "°F"
submit = st.sidebar.button("Get Forecast")

# Conversion helper (WeatherAPI returns C by default)
def convert_temp(temp_c):
    if units == "Celsius":
        return temp_c
    else:
        return temp_c * 9/5 + 32

if submit and city:
    # API call
    url = f'http://api.weatherapi.com/v1/forecast.json?key=058db954458f4f64941102840251207&q={city}&days=10&aqi=no&alerts=no'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        st.session_state["weather_data"] = data
        st.session_state["selected_day_index"] = None

    else:
        st.error("Invalid City Name")

        # Clear previous data
        if "weather_data" in st.session_state:
            del st.session_state["weather_data"]
        if "seven_days" in st.session_state:
            del st.session_state["seven_days"]
        if "selected_day_index" in st.session_state:
            del st.session_state["selected_day_index"]

if "weather_data" in st.session_state:
        data = st.session_state["weather_data"]
        loc = data["location"]
        date = datetime.strptime(loc['localtime'].split(' ')[0], "%Y-%m-%d")
        day = date.strftime("%A")
        current = data["current"]

        condition_text = current["condition"]["text"].lower()

        if "sunny" in condition_text or "clear" in condition_text:
            gradient = "linear-gradient(to bottom, #56ccf2, #2f80ed)"
        elif "cloud" in condition_text or "cloudy" or "overcast" in condition_text:
            gradient = "linear-gradient(to bottom, #bdc3c7, #2c3e50)"
        elif "rain" in condition_text or "drizzle" or "mist" in condition_text:
            gradient = "linear-gradient(to bottom, #bdc3c7, #2c3e50)"
        elif "storm" in condition_text or "thunder" in condition_text:
            gradient = "linear-gradient(to bottom, #bdc3c7, #2c3e50)"
        else:
            gradient = "linear-gradient(to bottom, #2980b9, #6dd5fa)"  # default bg


        st.markdown(
            f"""
            <style>
            .stApp {{
                background: {gradient};
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <div style='font-size: 40px; font-weight: 600;'>{f"{loc['name']}, {loc['country']}"}</div>
                <div style='font-size: 16px; color: #CCCCCC;'>Feels like {convert_temp(current['feelslike_c']):.1f}{unit_symbol}</div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 20px; font-weight: 500;'>{day}</div>
                <div style='font-size: 20px; font-weight: 500;'>{f"{loc['localtime'].split(' ')[1]}"}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True
        )

        st.divider()

        # Current weather
        icon = "https:" + current["condition"]["icon"]
        text = current["condition"]["text"]
        col1, col2,col3,col4,col5 = st.columns([1,1,1,1,1])

        with col1:
            st.markdown(
                f"""
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <img src="{icon}" style="width:64px;height:64px;">
                        <span style='font-size: 20px; font-weight: 500;'>{text}</span>
                    </div>""",
                unsafe_allow_html=True

            )

        with col2:
            st.metric("Current Temperature", f"{convert_temp(current['temp_c']):.1f}{unit_symbol}")
        with col3:
            st.metric("Humidity", f"{current['humidity']}%")
        with col4:
            st.metric("UV Index", current["uv"])
        with col5:
            st.metric("Wind Speed",f"{current['wind_kph']} km/h")


        st.divider()



        seven_days = data["forecast"]["forecastday"][:7]


        day_labels = []
        for i, d in enumerate(seven_days):
            if i == 0:
                day_labels.append("Today")
            else:
                dt = datetime.strptime(d["date"], "%Y-%m-%d")
                day_labels.append(dt.strftime("%A"))

        cols = st.columns(7)

        if "selected_day_index" not in st.session_state:
            st.session_state["selected_day_index"] = None

        for i, col in enumerate(cols):
            day = seven_days[i]
            with col:
                st.markdown(f"**{day_labels[i]}**")
                icon_url = "https:" + day["day"]["condition"]["icon"]
                st.image(icon_url, width=60)
                st.write(day["day"]["condition"]["text"])
                max_temp = day["day"]["maxtemp_c"]
                min_temp = day["day"]["mintemp_c"]
                st.write(f"{max_temp:.0f}°C / {min_temp:.0f}°C")

                if st.button("Details", key=f"details_{i}"):
                    st.session_state["selected_day_index"] = i

        # Check if any button was clicked
        if st.session_state["selected_day_index"] is not None:
            i = st.session_state["selected_day_index"]

            # day's data
            selected_day = seven_days[i]

            st.markdown("---")
            st.subheader(f"{day_labels[i]}")

            # hourly data
            hours = selected_day["hour"]
            times = [h["time"].split(" ")[1] for h in hours]
            temps = [h["temp_c"] for h in hours]
            precip = [h["precip_mm"] for h in hours]
            wind = [h["wind_kph"] for h in hours]
            humidity = [h["humidity"] for h in hours]


            option = st.selectbox(
                "Select parameter",
                ["Temperature", "Precipitation", "Wind", "Humidity"],
                key="param_select"
            )


            if option == "Temperature":

                fig = px.area(
                    x=times,
                    y=temps,
                    labels={'x': 'Time', 'y': 'Temperature (°C)'},
                    title="Hourly Temperature"
                )
                fig.update_traces(
                    line_color="orange",
                    fillcolor="rgba(255, 165, 0, 0.4)"
                )
                st.plotly_chart(fig, use_container_width=True)


            elif option == "Precipitation":
                fig = px.bar(
                    x=times,
                    y=precip,
                    labels={'x': 'Time', 'y': 'Precipitation (mm)'},
                    title="Hourly Precipitation"
                )
                st.plotly_chart(fig, use_container_width=True)

            elif option == "Wind":

                directions = [h["wind_degree"] for h in hours]
                speeds = [h["wind_kph"] for h in hours]


                hover = [
                    f"Time: {t}<br>Wind Speed: {s:.1f} km/h<br>Direction: {d}°"
                    for t, s, d in zip(times, speeds, directions)
                ]

                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=speeds,
                        mode='markers',
                        marker=dict(
                            symbol='arrow-up',
                            size=15,
                            angleref='previous',
                            angle=directions

                        ),
                        marker_color= 'white',
                        text=hover,
                        hoverinfo="text",
                        name='Wind Direction'
                    )
                )

                fig.update_layout(
                    title="Wind Speed and Direction",
                    yaxis_title="Wind Speed (km/h)",
                    xaxis_title="Time",
                )

                st.plotly_chart(fig, use_container_width=True)


            elif option == "Humidity":
                fig = px.line(
                    x=times,
                    y=humidity,
                    labels={'x': 'Time', 'y': 'Humidity (%)'},
                    title="Hourly Humidity"
                )
                st.plotly_chart(fig, use_container_width=True)




