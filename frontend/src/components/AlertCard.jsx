import { useEffect, useState } from "react";

import {
  AlertTriangle,
  CloudRain,
  Wind,
  ThermometerSun,
  CloudLightning,
  CheckCircle,
} from "lucide-react";


function AlertCard({
  latitude,
  longitude,
  locationName = "Selected Location",
}) {

  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);


  // ------------------------------------
  // Get weather data for alerts
  // ------------------------------------

  useEffect(() => {

    /*
      Do not use Mumbai as a fallback.

      Alerts must always use the coordinates
      received from App.jsx.
    */

    const getWeatherAlerts = async () => {

      try {

        setLoading(true);


        /*
          Fetch current + next 12 hours.

          These coordinates belong to the
          currently selected location.
        */

        const url =
          `https://api.open-meteo.com/v1/forecast` +
          `?latitude=${latitude}` +
          `&longitude=${longitude}` +
          `&current=temperature_2m,apparent_temperature,wind_speed_10m,weather_code` +
          `&hourly=precipitation_probability,precipitation,wind_speed_10m,weather_code,temperature_2m` +
          `&timezone=auto` +
          `&forecast_hours=12`;


        const response =
          await fetch(url);


        if (!response.ok) {

          throw new Error(
            "Unable to load alert data"
          );

        }


        const data =
          await response.json();


        const generatedAlerts = [];


        // ------------------------------------
        // Current conditions
        // ------------------------------------

        const currentTemperature =
          data.current?.temperature_2m;


        const currentWind =
          data.current?.wind_speed_10m;


        // ------------------------------------
        // Next 12 hours
        // ------------------------------------

        const precipitationProbability =
          data.hourly
            ?.precipitation_probability || [];


        const precipitation =
          data.hourly
            ?.precipitation || [];


        const windSpeed =
          data.hourly
            ?.wind_speed_10m || [];


        const weatherCodes =
          data.hourly
            ?.weather_code || [];


        const temperatures =
          data.hourly
            ?.temperature_2m || [];


        const maxRainProbability =
          precipitationProbability.length > 0
            ? Math.max(
                ...precipitationProbability
              )
            : 0;


        const maxRain =
          precipitation.length > 0
            ? Math.max(
                ...precipitation
              )
            : 0;


        const maxWind =
          windSpeed.length > 0
            ? Math.max(
                ...windSpeed
              )
            : currentWind || 0;


        const maxTemperature =
          temperatures.length > 0
            ? Math.max(
                ...temperatures
              )
            : currentTemperature;


        // ------------------------------------
        // Thunderstorm
        // ------------------------------------

        const hasThunderstorm =
          weatherCodes.some(
            (code) =>
              [95, 96, 99].includes(code)
          );


        if (hasThunderstorm) {

          generatedAlerts.push({

            type: "Thunderstorm Warning",

            location: locationName,

            description:
              `Thunderstorm conditions may occur in ${locationName} during the next few hours. Stay indoors when possible and avoid exposed areas.`,

            time:
              "Thunderstorm conditions detected in the next 12 hours",

            icon: CloudLightning,

            level: "warning",

          });

        }


        // ------------------------------------
        // Heavy Rain
        // ------------------------------------

        /*
          Heavy rain is based primarily on
          precipitation amount and rain codes,
          rather than probability alone.
        */

        const hasHeavyRainCode =
          weatherCodes.some(
            (code) =>
              [65, 82].includes(code)
          );


        if (
          maxRain >= 10 ||
          hasHeavyRainCode
        ) {

          generatedAlerts.push({

            type: "Heavy Rain Warning",

            location: locationName,

            description:
              `Heavy rainfall may occur in ${locationName}. Avoid unnecessary travel and stay away from waterlogged or low-lying areas.`,

            time:
              maxRain > 0
                ? `Maximum precipitation: ${maxRain.toFixed(1)} mm`
                : "Heavy rain conditions detected",

            icon: CloudRain,

            level: "warning",

          });

        }

        // ------------------------------------
        // Rain Advisory
        // ------------------------------------

        else if (
          maxRainProbability >= 60 ||
          maxRain >= 2
        ) {

          generatedAlerts.push({

            type: "Rain Advisory",

            location: locationName,

            description:
              `Rain is possible in ${locationName} during the next few hours. Consider carrying an umbrella and plan travel accordingly.`,

            time:
              `Rain probability may reach ${Math.round(
                maxRainProbability
              )}%`,

            icon: CloudRain,

            level: "advisory",

          });

        }


        // ------------------------------------
        // Strong Wind
        // ------------------------------------

        if (
          maxWind >= 40
        ) {

          generatedAlerts.push({

            type: "Strong Wind Advisory",

            location: locationName,

            description:
              `Strong winds may occur in ${locationName}. Secure loose objects and exercise caution while travelling.`,

            time:
              `Wind speed may reach ${Math.round(
                maxWind
              )} km/h`,

            icon: Wind,

            level: "advisory",

          });

        }


        // ------------------------------------
        // Extreme Heat
        // ------------------------------------

        if (
          maxTemperature >= 40
        ) {

          generatedAlerts.push({

            type: "Extreme Heat Warning",

            location: locationName,

            description:
              `Very high temperatures are expected in ${locationName}. Stay hydrated, avoid prolonged exposure to direct sunlight, and limit strenuous outdoor activity.`,

            time:
              `Temperature may reach ${Math.round(
                maxTemperature
              )}°C`,

            icon: ThermometerSun,

            level: "warning",

          });

        }


        // ------------------------------------
        // Set alerts
        // ------------------------------------

        setAlerts(
          generatedAlerts
        );


      } catch (error) {

        console.error(
          "Weather alert error:",
          error
        );

        setAlerts([]);

      } finally {

        setLoading(false);

      }

    };


    getWeatherAlerts();

  }, [
    latitude,
    longitude,
    locationName,
  ]);


  return (
    <section
      id="alerts"
      className="mt-6"
    >

      {/* -------------------------------- */}
      {/* Heading */}
      {/* -------------------------------- */}

      <div className="mb-4 flex items-end justify-between">

        <div>

          <h2 className="text-xl font-semibold tracking-tight">
            Alerts & advisories
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Important warnings and advisories for{" "}
            <span className="text-slate-300">
              {locationName}
            </span>
          </p>

        </div>


        {alerts.length > 0 && (

          <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs font-medium text-red-400">

            {alerts.length}{" "}
            {alerts.length === 1
              ? "Active"
              : "Active"}

          </span>

        )}

      </div>


      {/* -------------------------------- */}
      {/* Loading */}
      {/* -------------------------------- */}

      {loading && (

        <div className="glass-panel rounded-2xl p-6">

          <p className="text-slate-400">
            Checking weather conditions for{" "}
            {locationName}...
          </p>

        </div>

      )}


      {/* -------------------------------- */}
      {/* No Alerts */}
      {/* -------------------------------- */}

      {!loading &&
        alerts.length === 0 && (

          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/[.06] p-5">

            <div className="flex items-center gap-4">

              <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">

                <CheckCircle
                  size={24}
                />

              </div>


              <div>

                <h3 className="font-semibold text-emerald-300">
                  No Active Alerts
                </h3>

                <p className="mt-1 text-sm text-slate-400">

                  No significant weather
                  conditions are currently
                  detected for{" "}

                  <span className="text-slate-300">
                    {locationName}
                  </span>
                  .

                </p>

              </div>

            </div>

          </div>

        )}


      {/* -------------------------------- */}
      {/* Active Alerts */}
      {/* -------------------------------- */}

      {!loading &&
        alerts.length > 0 && (

          <div className="space-y-4">

            {alerts.map(
              (alert, index) => {

                const AlertIcon =
                  alert.icon;


                return (
                  <div
                    key={`${alert.type}-${index}`}
                    className={`rounded-2xl border p-5 shadow-lg shadow-slate-950/10 ${
                      alert.level ===
                      "warning"
                        ? "border-red-500/20 bg-red-500/5"
                        : "border-yellow-500/20 bg-yellow-500/5"
                    }`}
                  >

                    <div className="flex gap-4">

                      {/* Icon */}

                      <div
                        className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl ${
                          alert.level ===
                          "warning"
                            ? "bg-red-500/10 text-red-400"
                            : "bg-yellow-500/10 text-yellow-400"
                        }`}
                      >

                        <AlertIcon
                          size={24}
                        />

                      </div>


                      {/* Content */}

                      <div className="flex-1">

                        <div className="flex flex-wrap items-center justify-between gap-2">

                          <div>

                            <h3
                              className={`font-semibold ${
                                alert.level ===
                                "warning"
                                  ? "text-red-300"
                                  : "text-yellow-300"
                              }`}
                            >
                              {alert.type}
                            </h3>


                            <p className="mt-1 text-sm text-slate-400">
                              📍{" "}
                              {alert.location}
                            </p>

                          </div>


                          <span
                            className={`rounded-full px-3 py-1 text-xs font-medium ${
                              alert.level ===
                              "warning"
                                ? "bg-red-500/10 text-red-400"
                                : "bg-yellow-500/10 text-yellow-400"
                            }`}
                          >

                            {alert.level ===
                            "warning"
                              ? "WARNING"
                              : "ADVISORY"}

                          </span>

                        </div>


                        <p className="mt-4 text-sm leading-6 text-slate-300">
                          {alert.description}
                        </p>


                        <div className="mt-4 flex items-center gap-2 text-xs text-slate-400">

                          <AlertTriangle
                            size={14}
                          />

                          {alert.time}

                        </div>

                      </div>

                    </div>

                  </div>
                );

              }
            )}

          </div>

        )}

    </section>
  );
}


export default AlertCard;
