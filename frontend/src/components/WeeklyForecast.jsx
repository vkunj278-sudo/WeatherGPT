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

  if (code === 0) {
    return Sun;
  }

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


function WeeklyForecast({
  latitude,
  longitude,
  locationName,
  temperatureUnit = "C",
}) {

  const [weeklyData, setWeeklyData] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    const controller =
      new AbortController();


    const getWeeklyForecast = async () => {

      try {

        setLoading(true);
        setError("");


        const response = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto&forecast_days=7`,
          {
            signal:
              controller.signal,
          }
        );


        if (!response.ok) {
          throw new Error(
            "Weekly forecast could not be loaded"
          );
        }


        const data =
          await response.json();


        const days =
          data.daily.time.map(
            (date, index) => {

              return {

                date,

                high:
                  data.daily
                    .temperature_2m_max[
                    index
                  ],

                low:
                  data.daily
                    .temperature_2m_min[
                    index
                  ],

                weatherCode:
                  data.daily
                    .weather_code[
                    index
                  ],

                precipitationProbability:
                  data.daily
                    .precipitation_probability_max[
                    index
                  ],

              };

            }
          );


        setWeeklyData(days);

      } catch (err) {

        if (
          err.name !==
          "AbortError"
        ) {

          console.error(
            "Weekly forecast error:",
            err
          );

          setError(
            "Unable to load weekly forecast"
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


    getWeeklyForecast();


    return () =>
      controller.abort();

  }, [latitude, longitude]);


  const formatDay = (
    date,
    index
  ) => {

    if (index === 0) {
      return "Today";
    }


    const dateObject =
      new Date(
        `${date}T12:00:00`
      );


    return dateObject.toLocaleDateString(
      "en-IN",
      {
        weekday: "long",
      }
    );

  };


  if (loading) {

    return (
      <section>

        <div className="rounded-3xl border border-white/10 bg-slate-900/60 p-6">

          <p className="text-slate-400">
            Loading weekly forecast...
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

      <div className="mb-5">

        <h2 className="text-xl font-semibold">
          7-Day Forecast
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Extended weather forecast for {locationName}
        </p>

      </div>


      <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/60">

        {weeklyData.map(
          (day, index) => {

            const WeatherIcon =
              getWeatherIcon(
                day.weatherCode
              );


            const high =
              convertTemperature(
                day.high,
                temperatureUnit
              );


            const low =
              convertTemperature(
                day.low,
                temperatureUnit
              );


            return (

              <div
                key={day.date}
                className={`flex items-center justify-between px-5 py-5 sm:px-6 ${
                  index !== 0
                    ? "border-t border-slate-800"
                    : ""
                }`}
              >

                <div className="w-24 sm:w-28">

                  <p className="font-medium text-white">
                    {formatDay(
                      day.date,
                      index
                    )}
                  </p>

                </div>


                <div className="flex flex-1 items-center gap-4">

                  <WeatherIcon
                    size={27}
                    className="text-cyan-300"
                  />


                  <div>

                    <p className="text-sm text-slate-300">
                      {getWeatherDescription(
                        day.weatherCode
                      )}
                    </p>


                    <p className="mt-1 text-xs text-slate-500">

                      💧{" "}
                      {day.precipitationProbability ??
                        0}
                      % chance

                    </p>

                  </div>

                </div>


                <div className="flex w-24 justify-end gap-3">

                  <span className="font-semibold text-white">
                    {high}°
                  </span>

                  <span className="text-slate-500">
                    {low}°
                  </span>

                </div>

              </div>

            );

          }
        )}

      </div>

    </section>

  );

}


export default WeeklyForecast;