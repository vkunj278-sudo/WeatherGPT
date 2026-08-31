import { useState } from "react";

import {
  CloudSun,
  MapPin,
  Bell,
  Settings,
  X,
  Thermometer,
  BellRing,
  SlidersHorizontal,
} from "lucide-react";


function Navbar({
  locationName = "Bhavnagar",
  temperatureUnit,
  setTemperatureUnit,
}) {

  const [settingsOpen, setSettingsOpen] =
    useState(false);

  const [notificationsEnabled, setNotificationsEnabled] =
    useState(true);


  // ----------------------------------------
  // Scroll to section
  // ----------------------------------------

  const scrollToSection = (id) => {

    const section =
      document.getElementById(id);

    if (!section) {
      return;
    }

    const navbarHeight = 85;

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


  return (
    <>

      {/* =========================================
          NAVBAR
      ========================================= */}

      <nav
        className="
          sticky
          top-0
          z-50
          border-b
          border-white/5
          bg-[#050b16]/85
          backdrop-blur-xl
        "
      >

        <div
          className="
            mx-auto
            flex
            h-[76px]
            max-w-7xl
            items-center
            justify-between
            px-5
            sm:px-6
            lg:px-8
          "
        >

          {/* Logo */}

          <button
            type="button"
            onClick={() =>
              scrollToSection("dashboard")
            }
            className="group flex items-center gap-3"
          >

            <div
              className="
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-xl
                bg-gradient-to-br
                from-cyan-400
                to-blue-600
                shadow-lg
                shadow-cyan-500/20
                transition
                group-hover:scale-105
              "
            >

              <CloudSun
                size={23}
                className="text-white"
              />

            </div>


            <div className="hidden text-left sm:block">

              <h1 className="text-base font-semibold">
                WeatherGPT
              </h1>

              <p className="text-[11px] text-slate-500">
                Weather Intelligence
              </p>

            </div>

          </button>


          {/* Navigation */}

          <div className="hidden items-center gap-1 md:flex">

            <NavButton
              label="Dashboard"
              onClick={() =>
                scrollToSection("dashboard")
              }
            />

            <NavButton
              label="Forecast"
              onClick={() =>
                scrollToSection("forecast")
              }
            />

            <NavButton
              label="Alerts"
              onClick={() =>
                scrollToSection("alerts")
              }
            />

            <NavButton
              label="AI Chat"
              onClick={() =>
                scrollToSection("chat")
              }
            />

          </div>


          {/* Right side */}

          <div className="flex items-center gap-1.5">

            {/* Location */}

            <button
              type="button"
              onClick={() =>
                scrollToSection("weather-map")
              }
              className="
                hidden
                items-center
                gap-2
                rounded-xl
                border
                border-white/10
                bg-white/[0.03]
                px-3
                py-2
                text-sm
                text-slate-300
                transition
                hover:border-cyan-400/30
                hover:bg-cyan-400/5
                hover:text-white
                sm:flex
              "
            >

              <MapPin
                size={15}
                className="text-cyan-400"
              />

              {locationName}

            </button>


            {/* Alerts */}

            <button
              type="button"
              onClick={() =>
                scrollToSection("alerts")
              }
              className="
                rounded-xl
                p-2.5
                text-slate-400
                transition
                hover:bg-white/5
                hover:text-white
              "
              title="Weather alerts"
            >

              <Bell size={19} />

            </button>


            {/* Settings */}

            <button
              type="button"
              onClick={() =>
                setSettingsOpen(true)
              }
              className={`
                rounded-xl
                p-2.5
                transition
                ${
                  settingsOpen
                    ? "bg-cyan-400/10 text-cyan-300"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }
              `}
              title="Settings"
            >

              <Settings size={19} />

            </button>

          </div>

        </div>

      </nav>


      {/* =========================================
          SETTINGS
      ========================================= */}

      {settingsOpen && (

        <div
          className="
            fixed
            inset-0
            z-[100]
            flex
            items-start
            justify-center
            bg-black/50
            px-4
            pt-24
            backdrop-blur-sm
            sm:justify-end
            sm:pr-6
          "
          onClick={() =>
            setSettingsOpen(false)
          }
        >

          <div
            className="
              w-full
              max-w-md
              overflow-hidden
              rounded-3xl
              border
              border-white/10
              bg-[#0a1222]/95
              shadow-2xl
              shadow-black/40
            "
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            {/* Header */}

            <div className="flex items-center justify-between border-b border-white/[0.07] px-6 py-5">

              <div className="flex items-center gap-3">

                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">

                  <SlidersHorizontal size={18} />

                </div>

                <div>

                  <h2 className="text-lg font-semibold text-white">
                    Settings
                  </h2>

                  <p className="text-xs text-slate-500">
                    Customize your weather dashboard
                  </p>

                </div>

              </div>


              <button
                type="button"
                onClick={() =>
                  setSettingsOpen(false)
                }
                className="rounded-xl p-2 text-slate-400 transition hover:bg-white/5 hover:text-white"
                title="Close settings"
              >

                <X size={19} />

              </button>

            </div>


            {/* Content */}

            <div className="space-y-4 p-6">


              {/* Temperature Unit */}

              <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">

                <div className="flex items-start gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-400/10 text-sky-300">

                    <Thermometer size={18} />

                  </div>


                  <div>

                    <p className="text-sm font-medium text-white">
                      Temperature unit
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      Choose how temperatures are displayed throughout the dashboard.
                    </p>

                  </div>

                </div>


                <div className="mt-4 grid grid-cols-2 gap-2">

                  <button
                    type="button"
                    onClick={() =>
                      setTemperatureUnit("C")
                    }
                    className={`
                      rounded-xl
                      border
                      px-4
                      py-3
                      text-sm
                      font-medium
                      transition
                      ${
                        temperatureUnit === "C"
                          ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-300"
                          : "border-white/[0.07] bg-white/[0.02] text-slate-400 hover:text-white"
                      }
                    `}
                  >

                    Celsius

                    <span className="ml-1">
                      °C
                    </span>

                  </button>


                  <button
                    type="button"
                    onClick={() =>
                      setTemperatureUnit("F")
                    }
                    className={`
                      rounded-xl
                      border
                      px-4
                      py-3
                      text-sm
                      font-medium
                      transition
                      ${
                        temperatureUnit === "F"
                          ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-300"
                          : "border-white/[0.07] bg-white/[0.02] text-slate-400 hover:text-white"
                      }
                    `}
                  >

                    Fahrenheit

                    <span className="ml-1">
                      °F
                    </span>

                  </button>

                </div>

              </div>


              {/* Notifications */}

              <div className="flex items-center justify-between rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">

                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-300">

                    <BellRing size={18} />

                  </div>


                  <div>

                    <p className="text-sm font-medium text-white">
                      Weather alerts
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Show important weather warnings.
                    </p>

                  </div>

                </div>


                <button
                  type="button"
                  onClick={() =>
                    setNotificationsEnabled(
                      !notificationsEnabled
                    )
                  }
                  className={`
                    relative
                    h-6
                    w-11
                    rounded-full
                    transition
                    ${
                      notificationsEnabled
                        ? "bg-cyan-400"
                        : "bg-slate-700"
                    }
                  `}
                >

                  <span
                    className={`
                      absolute
                      top-1
                      h-4
                      w-4
                      rounded-full
                      bg-white
                      shadow
                      transition
                      ${
                        notificationsEnabled
                          ? "left-6"
                          : "left-1"
                      }
                    `}
                  />

                </button>

              </div>


              {/* Current selection */}

              <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">

                <div className="flex items-center justify-between">

                  <div>

                    <p className="text-xs text-slate-500">
                      Current temperature format
                    </p>

                    <p className="mt-1 text-sm font-semibold text-white">
                      {temperatureUnit === "C"
                        ? "Celsius (°C)"
                        : "Fahrenheit (°F)"}
                    </p>

                  </div>

                  <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-300">
                    Active
                  </span>

                </div>

              </div>

            </div>


            {/* Footer */}

            <div className="border-t border-white/[0.07] px-6 py-4">

              <p className="text-center text-[11px] text-slate-600">
                Temperature settings apply instantly.
              </p>

            </div>

          </div>

        </div>

      )}

    </>

  );
}


// ============================================
// Navigation Button
// ============================================

function NavButton({
  label,
  onClick,
}) {

  return (

    <button
      type="button"
      onClick={onClick}
      className="
        rounded-xl
        px-4
        py-2
        text-sm
        font-medium
        text-slate-400
        transition
        hover:bg-white/5
        hover:text-white
      "
    >

      {label}

    </button>

  );

}


export default Navbar;