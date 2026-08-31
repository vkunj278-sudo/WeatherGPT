import { useEffect, useState } from "react";

import {
  Sun,
  CloudSun,
  Cloud,
  CloudRain,
  CloudLightning,
  CloudFog,
} from "lucide-react";


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


const getWeatherDescription = (code) => {

  if (code === 0) return "Clear Sky";

  if ([1, 2].includes(code)) {
    return "Partly Cloudy";
  }

  if (code === 3) {
    return "Cloudy";
  }

  if ([45, 48].includes(code)) {
    return "Foggy";
  }

  if ([51, 53, 55].includes(code)) {
    return "Drizzle";
  }

  if ([61, 63, 65].includes(code)) {
    return "Rain";
  }

  if ([71, 73, 75].includes(code)) {
    return "Snow";
  }

  if ([80, 81, 82].includes(code)) {
    return "Rain Showers";
  }

  if ([95, 96, 99].includes(code)) {
    return "Thunderstorm";
  }

  return "Unknown";
};


const getWeatherIcon = (code) => {

  if (code === 0) return Sun;

  if ([1, 2].includes(code)) {
    return CloudSun;
  }

  if (code === 3) {
    return Cloud;
  }

  if ([45, 48].includes(code)) {
    return CloudFog;
  }

  if (
    [
      51,
      53,
      55,
      61,
      63,
      65,
      80,
      81,
      82,
    ].includes(code)
  ) {
    return CloudRain;
  }

  if ([95, 96, 99].includes(code)) {
    return CloudLightning;
  }

  return CloudSun;
};


function HourlyForecast({
  latitude,
  longitude,
  locationName,
  temperatureUnit = "C",
}) {

  const [hourlyData, setHourlyData] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    const controller =
      new AbortController();


    const getHourlyForecast = async () => {

      try {

        setLoading(true);
        setError("");


        const response = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&hourly=temperature_2m,relative_humidity_2m,weather_code&current=temperature_2m,weather_code&timezone=auto&forecast_days=2`,
          {
            signal:
              controller.signal,
          }
        );


        if (!response.ok) {
          throw new Error(
            "Hourly forecast could not be loaded"
          );
        }


        const data =
          await response.json();


        const currentTime =
          data.current.time;


        let currentIndex =
          data.hourly.time.findIndex(
            (time) =>
              time === currentTime
          );


        if (currentIndex === -1) {

          const currentHour =
            currentTime.slice(0, 13);


          currentIndex =
            data.hourly.time.findIndex(
              (time) =>
                time.slice(0, 13) ===
                currentHour
            );

        }


        if (currentIndex === -1) {

          throw new Error(
            "Current forecast time not found"
          );

        }


        const hours =
          data.hourly.time
            .slice(
              currentIndex,
              currentIndex + 12
            )
            .map(
              (time, index) => {

                const originalIndex =
                  currentIndex + index;


                return {

                  time,

                  temperature:
                    data.hourly
                      .temperature_2m[
                      originalIndex
                    ],

                  humidity:
                    data.hourly
                      .relative_humidity_2m[
                      originalIndex
                    ],

                  weatherCode:
                    data.hourly
                      .weather_code[
                      originalIndex
                    ],

                };

              }
            );


        setHourlyData(hours);

      } catch (err) {

        if (
          err.name !==
          "AbortError"
        ) {

          console.error(
            "Hourly forecast error:",
            err
          );

          setError(
            "Unable to load hourly forecast"
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


    getHourlyForecast();


    return () =>
      controller.abort();

  }, [latitude, longitude]);


  const formatTime = (
    time,
    index
  ) => {

    if (index === 0) {
      return "Now";
    }


    const hour = parseInt(
      time.slice(11, 13),
      10
    );


    if (hour === 0) {
      return "12 AM";
    }


    if (hour === 12) {
      return "12 PM";
    }


    if (hour > 12) {
      return `${hour - 12} PM`;
    }


    return `${hour} AM`;

  };


  if (loading) {

    return (
      <section>

        <div className="rounded-3xl border border-white/10 bg-slate-900/60 p-6">

          <p className="text-slate-400">
            Loading hourly forecast...
          </p>

        </div>

      </section>
    );

  }


  if (error) {

    return (
      <section>

        <div className="rounded-3xl border border-rose-400/20 bg-rose-400/5 p-6">

          <p className="text-rose-300">
            {error}
          </p>

        </div>

      </section>
    );

  }


  return (

    <section>

      <div className="mb-5 flex items-end justify-between">

        <div>

          <h2 className="text-xl font-semibold">
            Next 12 hours
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Temperature trend in {locationName}
          </p>

        </div>


        <span className="rounded-full bg-cyan-400/10 px-3 py-1.5 text-xs font-medium text-cyan-300">
          Live forecast
        </span>

      </div>


      {/* Forecast card */}

      <div className="overflow-x-auto rounded-3xl border border-white/10 bg-slate-900/60">

        <div className="grid min-w-[1200px] grid-cols-12">

          {hourlyData.map(
            (hour, index) => {

              const WeatherIcon =
                getWeatherIcon(
                  hour.weatherCode
                );


              const temperature =
                convertTemperature(
                  hour.temperature,
                  temperatureUnit
                );


              return (

                <div
                  key={hour.time}
                  className={`p-4 text-center ${
                    index !== 0
                      ? "border-l border-slate-800"
                      : ""
                  }`}
                >

                  <p className="text-xs font-medium text-slate-300">
                    {formatTime(
                      hour.time,
                      index
                    )}
                  </p>


                  <div className="my-4 flex justify-center">

                    <WeatherIcon
                      size={25}
                      className="text-cyan-300"
                    />

                  </div>


                  <p className="text-xl font-semibold">
                    {temperature}°
                  </p>


                  <p className="mt-2 text-[11px] text-slate-500">
                    {getWeatherDescription(
                      hour.weatherCode
                    )}
                  </p>


                  <p className="mt-2 text-xs text-slate-500">
                    💧 {hour.humidity}%
                  </p>

                </div>

              );

            }
          )}

        </div>

      </div>

    </section>

  );

}


export default HourlyForecast;