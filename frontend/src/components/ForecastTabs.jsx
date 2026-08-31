import {
  CalendarDays,
  Clock3,
} from "lucide-react";

import HourlyForecast from "./HourlyForecast";
import WeeklyForecast from "./WeeklyForecast";


function ForecastTabs({
  latitude,
  longitude,
  locationName,
  activeTab,
  setActiveTab,
  temperatureUnit = "C",
}) {

  const tabs = [
    {
      id: "hourly",
      label: "Hourly",
      icon: Clock3,
    },
    {
      id: "weekly",
      label: "7 days",
      icon: CalendarDays,
    },
  ];


  return (
    <section
      id="forecast"
      className="mt-8 scroll-mt-28"
    >

      {/* ----------------------------------------
          Forecast Header
      ---------------------------------------- */}

      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">

        <div>

          <p className="text-sm font-medium text-cyan-300">
            Outlook
          </p>

          <h2 className="mt-1 text-2xl font-semibold tracking-tight">
            Forecast
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            A clear view of what comes next.
          </p>

        </div>


        {/* ----------------------------------------
            Forecast Tabs
        ---------------------------------------- */}

        <div className="flex gap-2 rounded-xl border border-slate-800 bg-slate-900/70 p-1.5 shadow-lg backdrop-blur-md">

          {tabs.map(
            ({
              id,
              label,
              icon: Icon,
            }) => (

              <button
                key={id}
                type="button"
                onClick={() =>
                  setActiveTab(id)
                }
                className={`
                  inline-flex
                  items-center
                  gap-2
                  rounded-lg
                  px-5
                  py-2.5
                  text-sm
                  font-medium
                  transition-all
                  duration-200

                  ${
                    activeTab === id
                      ? "bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }
                `}
              >

                <Icon size={16} />

                {label}

              </button>

            )
          )}

        </div>

      </div>


      {/* ----------------------------------------
          Selected Forecast
      ---------------------------------------- */}

      {activeTab === "hourly" ? (

        <HourlyForecast
          latitude={latitude}
          longitude={longitude}
          locationName={locationName}
          temperatureUnit={temperatureUnit}
        />

      ) : (

        <WeeklyForecast
          latitude={latitude}
          longitude={longitude}
          locationName={locationName}
          temperatureUnit={temperatureUnit}
        />

      )}

    </section>
  );
}


export default ForecastTabs;