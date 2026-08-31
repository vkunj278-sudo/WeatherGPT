import { useEffect, useState } from "react";

import {
  Cloud,
  CloudRain,
  CloudSun,
  Droplets,
  Eye,
  Gauge,
  MapPin,
  Sun,
  Thermometer,
  Wind,
  Clock3,
  CalendarDays,
  ArrowUpRight,
} from "lucide-react";


const condition = (code) => {

  if (code === 0) {
    return ["Clear skies", Sun];
  }

  if ([1, 2].includes(code)) {
    return ["Partly cloudy", CloudSun];
  }

  if (code === 3) {
    return ["Overcast", Cloud];
  }

  if ([45, 48].includes(code)) {
    return ["Misty", Cloud];
  }

  if (
    [
      51,
      53,
      55,
      56,
      57,
      61,
      63,
      65,
      66,
      67,
      80,
      81,
      82,
    ].includes(code)
  ) {
    return ["Rain showers", CloudRain];
  }

  if ([95, 96, 99].includes(code)) {
    return ["Thunderstorms", CloudRain];
  }

  return ["Mixed conditions", CloudSun];
};


// ----------------------------------------
// Convert Celsius
// ----------------------------------------

const convertTemperature = (
  celsius,
  unit
) => {

  if (unit === "F") {
    return Math.round(
      (celsius * 9) / 5 + 32
    );
  }

  return Math.round(celsius);
};


const getTemperatureSymbol = (unit) =>
  unit === "F" ? "°F" : "°C";


// ----------------------------------------
// Scroll forecast
// ----------------------------------------

const scrollToForecast = () => {

  const section =
    document.getElementById("forecast");

  if (!section) {
    return;
  }

  const navbarHeight = 90;

  const sectionPosition =
    section.getBoundingClientRect().top +
    window.scrollY;

  window.scrollTo({
    top:
      sectionPosition -
      navbarHeight,
    behavior: "smooth",
  });

};


function WeatherCard({
  latitude,
  longitude,
  locationName,
  temperatureUnit = "C",
  onForecastClick,
  onWeeklyClick,
}) {

  const [weather, setWeather] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    const controller =
      new AbortController();


    const getWeather = async () => {

      try {

        setLoading(true);
        setError("");


        const response = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,surface_pressure,visibility&timezone=auto`,
          {
            signal:
              controller.signal,
          }
        );


        if (!response.ok) {
          throw new Error(
            "Weather data could not be loaded"
          );
        }


        const data =
          await response.json();


        setWeather(data.current);

      } catch (err) {

        if (
          err.name !==
          "AbortError"
        ) {

          console.error(
            "Weather API error:",
            err
          );

          setError(
            "Live weather data is temporarily unavailable."
          );

        }

      } finally {

        if (
          !controller.signal.aborted
        ) {

          setLoading(false);

        }

      }

    };


    getWeather();


    return () =>
      controller.abort();

  }, [latitude, longitude]);


  if (loading) {

    return (
      <div className="mt-2 h-[22rem] animate-pulse rounded-3xl border border-white/10 bg-slate-900/50" />
    );

  }


  if (error || !weather) {

    return (
      <div className="mt-2 rounded-3xl border border-rose-400/20 bg-rose-400/5 p-6 text-rose-200">

        {error ||
          "Weather data unavailable"}

      </div>
    );

  }


  const [
    description,
    WeatherIcon,
  ] = condition(
    weather.weather_code
  );


  const temperature =
    convertTemperature(
      weather.temperature_2m,
      temperatureUnit
    );


  const feelsLike =
    convertTemperature(
      weather.apparent_temperature,
      temperatureUnit
    );


  const symbol =
    getTemperatureSymbol(
      temperatureUnit
    );


  const metrics = [

    [
      Droplets,
      "Humidity",
      `${weather.relative_humidity_2m}%`,
    ],

    [
      Wind,
      "Wind",
      `${Math.round(
        weather.wind_speed_10m
      )} km/h`,
    ],

    [
      Eye,
      "Visibility",
      `${Math.round(
        weather.visibility / 1000
      )} km`,
    ],

    [
      Gauge,
      "Pressure",
      `${Math.round(
        weather.surface_pressure
      )} hPa`,
    ],

  ];


  return (

    <section className="relative overflow-hidden rounded-3xl border border-sky-300/15 bg-[linear-gradient(120deg,rgba(14,116,144,.38),rgba(30,41,59,.88)_48%,rgba(49,46,129,.4))] p-5 shadow-2xl shadow-slate-950/30 sm:p-8">


      <div className="pointer-events-none absolute -right-16 -top-20 h-64 w-64 rounded-full bg-sky-300/15 blur-3xl" />

      <div className="pointer-events-none absolute -bottom-24 -left-20 h-60 w-60 rounded-full bg-blue-500/10 blur-3xl" />


      {/* Location */}

      <div className="relative flex flex-wrap items-center justify-between gap-3 text-sm">

        <div className="flex items-center gap-2 font-medium text-sky-100">

          <span className="grid h-8 w-8 place-items-center rounded-full bg-white/10">

            <MapPin size={15} />

          </span>

          {locationName}, India

        </div>


        <span className="rounded-full border border-white/10 bg-slate-950/20 px-3 py-1.5 text-xs text-slate-300">

          Updated just now

        </span>

      </div>


      {/* Main */}

      <div className="relative mt-8 grid gap-8 lg:grid-cols-[1fr_25rem] lg:items-center">


        {/* Temperature */}

        <div className="flex items-center gap-4 sm:gap-6">

          <div className="grid h-24 w-24 shrink-0 place-items-center rounded-[1.75rem] border border-white/15 bg-white/10 shadow-inner shadow-sky-100/10 sm:h-28 sm:w-28">

            <WeatherIcon
              className="text-amber-200"
              size={56}
              strokeWidth={1.5}
            />

          </div>


          <div>

            <div className="flex items-start">

              <span className="text-6xl font-semibold tracking-tighter sm:text-7xl">

                {temperature}°

              </span>

              <span className="mt-2 text-lg text-slate-300">
                {symbol.replace("°", "")}
              </span>

            </div>


            <p className="mt-1 text-lg font-medium text-white">
              {description}
            </p>


            <p className="mt-1 text-sm text-sky-100/70">

              Feels like {feelsLike}
              {symbol}

            </p>

          </div>

        </div>


        {/* Forecast preview */}

        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-slate-950/30 p-5 shadow-xl backdrop-blur-md">

          <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full bg-cyan-400/10 blur-2xl" />


          <div className="relative flex items-start justify-between">

            <div>

              <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                Weather intelligence
              </p>

              <p className="mt-2 text-sm text-slate-400">
                Planning your day in
              </p>

              <h3 className="mt-1 text-xl font-bold text-white">
                {locationName}
              </h3>

            </div>


            <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5">

              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />

              <span className="text-[10px] font-bold tracking-wider text-emerald-300">
                LIVE
              </span>

            </div>

          </div>


          {/* Forecast buttons */}

          <div className="relative mt-6 grid grid-cols-2 gap-3">

            <button
              type="button"
              onClick={() => {

                onForecastClick();

                scrollToForecast();

              }}
              className="group relative overflow-hidden rounded-2xl border border-slate-700/70 bg-slate-800/50 p-4 text-left transition-all duration-300 hover:-translate-y-1 hover:border-cyan-400/50 hover:bg-slate-800/80 hover:shadow-lg hover:shadow-cyan-500/10"
            >

              <div className="flex items-center justify-between">

                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">

                  <Clock3 size={18} />

                </div>

                <ArrowUpRight
                  size={17}
                  className="text-slate-600 group-hover:text-cyan-300"
                />

              </div>


              <p className="mt-4 text-xs text-slate-500">
                Forecast
              </p>

              <p className="mt-1 text-base font-semibold text-white">
                Next 12 hours
              </p>

              <p className="mt-2 text-xs text-slate-500">
                Hourly conditions
              </p>

            </button>


            <button
              type="button"
              onClick={() => {

                onWeeklyClick();

                scrollToForecast();

              }}
              className="group relative overflow-hidden rounded-2xl border border-slate-700/70 bg-slate-800/50 p-4 text-left transition-all duration-300 hover:-translate-y-1 hover:border-blue-400/50 hover:bg-slate-800/80 hover:shadow-lg hover:shadow-blue-500/10"
            >

              <div className="flex items-center justify-between">

                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-400/10 text-blue-300">

                  <CalendarDays size={18} />

                </div>

                <ArrowUpRight
                  size={17}
                  className="text-slate-600 group-hover:text-blue-300"
                />

              </div>


              <p className="mt-4 text-xs text-slate-500">
                Outlook
              </p>

              <p className="mt-1 text-base font-semibold text-white">
                7 days
              </p>

              <p className="mt-2 text-xs text-slate-500">
                Extended forecast
              </p>

            </button>

          </div>


          <div className="relative mt-5 flex items-center gap-2 text-xs text-slate-500">

            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />

            Click a forecast to explore

            <ArrowUpRight size={13} />

          </div>

        </div>

      </div>


      {/* Metrics */}

      <div className="relative mt-8 grid grid-cols-2 gap-2 border-t border-white/10 pt-5 sm:grid-cols-4 sm:gap-3">

        {metrics.map(
          ([Icon, label, value]) => (

            <div
              key={label}
              className="rounded-2xl bg-slate-950/20 p-3.5 sm:p-4"
            >

              <Icon
                size={17}
                className="text-sky-300"
              />

              <p className="mt-3 text-xs text-slate-400">
                {label}
              </p>

              <p className="mt-1 font-semibold text-white">
                {value}
              </p>

            </div>

          )
        )}

      </div>

    </section>

  );
}


export default WeatherCard;