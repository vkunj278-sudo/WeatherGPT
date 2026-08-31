import { useState } from "react";

import Navbar from "./components/Navbar";
import WeatherCard from "./components/WeatherCard";
import ForecastTabs from "./components/ForecastTabs";
import AlertCard from "./components/AlertCard";
import ChatBox from "./components/ChatBox";
import WeatherMap from "./components/WeatherMap";


function App() {

  // ----------------------------------------
  // Current selected location
  // ----------------------------------------

  const [position, setPosition] = useState([
    21.7645,
    72.1519,
  ]);

  const [locationName, setLocationName] =
    useState("Bhavnagar");


  // ----------------------------------------
  // Selected forecast tab
  // ----------------------------------------

  const [forecastTab, setForecastTab] =
    useState("hourly");


  // ----------------------------------------
  // Temperature unit
  //
  // C = Celsius
  // F = Fahrenheit
  // ----------------------------------------

  const [temperatureUnit, setTemperatureUnit] =
    useState("C");


  return (
    <div className="min-h-screen bg-slate-950 text-white">


      {/* ========================================
          NAVBAR
      ======================================== */}

      <Navbar
        locationName={locationName}
        temperatureUnit={temperatureUnit}
        setTemperatureUnit={setTemperatureUnit}
      />


      {/* ========================================
          MAIN CONTENT
      ======================================== */}

      <main
        className="
          mx-auto
          max-w-7xl
          px-5
          pb-20
          pt-10
          sm:px-6
          lg:px-8
        "
      >


        {/* ========================================
            DASHBOARD
        ======================================== */}

        <section
          id="dashboard"
          className="scroll-mt-28"
        >

          <div className="mb-8">

            <p className="text-sm font-medium text-cyan-300">
              Live local intelligence
            </p>


            <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">

              Weather intelligence

              <br />

              <span className="text-cyan-400">
                for your day.
              </span>

            </h1>


            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-400">

              Real-time conditions, hourly forecasts,
              alerts and AI-powered weather guidance
              — all in one focused dashboard.

            </p>


            <div className="mt-6 flex flex-wrap items-center gap-3">

              <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-300">

                <span className="text-cyan-400">
                  📍
                </span>

                {locationName}

              </div>


              <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-4 py-2 text-sm text-emerald-300">

                <span className="h-2 w-2 rounded-full bg-emerald-400" />

                Live data

              </div>

            </div>

          </div>


          {/* Current Weather */}

          <WeatherCard
            latitude={position[0]}
            longitude={position[1]}
            locationName={locationName}
            temperatureUnit={temperatureUnit}
            onForecastClick={() => {
              setForecastTab("hourly");
            }}
            onWeeklyClick={() => {
              setForecastTab("weekly");
            }}
          />

        </section>


        {/* ========================================
            FORECAST
        ======================================== */}

        <section
          className="mt-20 scroll-mt-28"
        >

          <ForecastTabs
            latitude={position[0]}
            longitude={position[1]}
            locationName={locationName}
            activeTab={forecastTab}
            setActiveTab={setForecastTab}
            temperatureUnit={temperatureUnit}
          />

        </section>


        {/* ========================================
            ALERTS
        ======================================== */}

        <section
          id="alerts"
          className="mt-20 scroll-mt-28"
        >

          <AlertCard
            locationName={locationName}
            latitude={position[0]}
            longitude={position[1]}
          />

        </section>


        {/* ========================================
            CHAT
        ======================================== */}

        <section
          id="chat"
          className="mt-24 scroll-mt-28"
        >

          <ChatBox
            latitude={position[0]}
            longitude={position[1]}
            locationName={locationName}
            temperatureUnit={temperatureUnit}
          />

        </section>


        {/* ========================================
            WEATHER MAP
        ======================================== */}

        <section
          id="weather-map"
          className="mt-24 scroll-mt-28"
        >

          <WeatherMap
            position={position}
            setPosition={setPosition}
            locationName={locationName}
            setLocationName={setLocationName}
          />

        </section>


        <div className="h-10" />

      </main>

    </div>
  );
}


export default App;