import { useState, useEffect } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";

import {
  Search,
  MapPin,
  Navigation,
  LocateFixed,
} from "lucide-react";

import "leaflet/dist/leaflet.css";


// ------------------------------------
// Map Controller
// ------------------------------------
function MapController({ position }) {
  const map = useMap();

  useEffect(() => {
    map.setView(position, 10);
  }, [position, map]);

  return null;
}


// ------------------------------------
// Use My Location Button
// ------------------------------------
function LocationController({ onLocationFound }) {
  const map = useMap();

  const findMyLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;

        map.setView(
          [latitude, longitude],
          12,
          {
            animate: true,
          }
        );

        onLocationFound(latitude, longitude);
      },

      () => {
        alert(
          "Unable to get your location. Please allow location access in your browser."
        );
      }
    );
  };

  return (
    <div className="absolute right-4 top-4 z-[1000]">

      <button
        className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-950/90 px-4 py-3 text-sm font-medium text-white shadow-xl backdrop-blur-md transition hover:border-sky-400/40 hover:bg-slate-900"
        onClick={findMyLocation}
        type="button"
      >

        <LocateFixed
          size={17}
          className="text-sky-400"
        />

        <span>
          Use My Location
        </span>

      </button>

    </div>
  );
}


// ------------------------------------
// Weather Map
// ------------------------------------
function WeatherMap({
  position,
  setPosition,
  locationName,
  setLocationName,
}) {

  const [location, setLocation] =
    useState(locationName);

  const [searching, setSearching] =
    useState(false);


  // ------------------------------------
  // Keep input synchronized
  // ------------------------------------
  useEffect(() => {
    setLocation(locationName);
  }, [locationName]);


  // ------------------------------------
  // Search Location
  // ------------------------------------
  const searchLocation = async () => {

    if (!location.trim() || searching) {
      return;
    }

    try {

      setSearching(true);

      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          location
        )}`
      );

      if (!response.ok) {
        throw new Error(
          "Location search failed"
        );
      }

      const data = await response.json();

      if (data.length === 0) {
        alert("Location not found");
        return;
      }

      const latitude =
        parseFloat(data[0].lat);

      const longitude =
        parseFloat(data[0].lon);

      const newPosition = [
        latitude,
        longitude,
      ];

      setPosition(newPosition);

      const cityName =
        data[0].display_name
          .split(",")[0]
          .trim();

      setLocationName(cityName);

      setLocation(cityName);

    } catch (error) {

      console.error(
        "Location search failed:",
        error
      );

      alert(
        "Unable to search location"
      );

    } finally {

      setSearching(false);

    }
  };


  // ------------------------------------
  // Enter Key Search
  // ------------------------------------
  const handleKeyDown = (event) => {

    if (event.key === "Enter") {
      searchLocation();
    }

  };


  // ------------------------------------
  // Current Location
  // ------------------------------------
  const handleMyLocation = async (
    latitude,
    longitude
  ) => {

    setPosition([
      latitude,
      longitude,
    ]);

    try {

      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
      );

      if (!response.ok) {
        throw new Error(
          "Reverse geocoding failed"
        );
      }

      const data =
        await response.json();

      const city =
        data.address?.city ||
        data.address?.town ||
        data.address?.village ||
        data.address?.municipality ||
        "My Location";

      setLocationName(city);

      setLocation(city);

    } catch (error) {

      console.error(
        "Reverse geocoding failed:",
        error
      );

      setLocationName(
        "My Location"
      );

      setLocation(
        "My Location"
      );

    }

  };


  return (
    <section
      className="mt-12"
      id="weather-map"
    >

      {/* -------------------------------- */}
      {/* Section Header */}
      {/* -------------------------------- */}

      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">

        <div>

          {/* Small label */}

          <div className="mb-2 flex items-center gap-2">

            <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]" />

            <span className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-300">
              Live map
            </span>

          </div>


          {/* Main heading */}

          <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
            Weather Map
          </h2>


          {/* Subtitle */}

          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
            Explore weather conditions and locations
            with an interactive map.
          </p>

        </div>


        {/* Current location badge */}

        <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-slate-900/70 px-3 py-2 text-xs text-slate-300 backdrop-blur-sm sm:flex">

          <MapPin
            size={14}
            className="text-sky-400"
          />

          <span>
            {locationName}
          </span>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* Search Area */}
      {/* -------------------------------- */}

      <div className="mb-5 rounded-2xl border border-white/10 bg-slate-900/60 p-2 shadow-lg shadow-black/10 backdrop-blur-md">

        <div className="flex flex-col gap-2 sm:flex-row">

          {/* Input */}

          <div className="relative flex-1">

            <Search
              size={18}
              className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
            />

            <input
              type="text"
              placeholder="Search for a city or location..."
              value={location}
              onChange={(event) =>
                setLocation(
                  event.target.value
                )
              }
              onKeyDown={handleKeyDown}
              className="h-12 w-full rounded-xl border border-transparent bg-slate-950/60 pl-11 pr-4 text-sm text-white outline-none placeholder:text-slate-500 transition focus:border-sky-400/40 focus:bg-slate-950"
            />

          </div>


          {/* Search button */}

          <button
            onClick={searchLocation}
            disabled={searching}
            type="button"
            className="flex h-12 items-center justify-center gap-2 rounded-xl bg-sky-400 px-6 text-sm font-semibold text-slate-950 transition hover:bg-sky-300 disabled:cursor-not-allowed disabled:opacity-60"
          >

            <Search size={17} />

            {searching
              ? "Searching..."
              : "Search"}

          </button>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* Map Card */}
      {/* -------------------------------- */}

      <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-slate-900 p-2 shadow-2xl shadow-black/20">

        {/* Small map header */}

        <div className="absolute left-5 top-5 z-[1000] rounded-xl border border-white/10 bg-slate-950/85 px-3 py-2 text-xs font-medium text-slate-200 shadow-lg backdrop-blur-md">

          <div className="flex items-center gap-2">

            <Navigation
              size={14}
              className="text-sky-400"
            />

            {locationName}

          </div>

        </div>


        {/* Map */}

        <div className="h-[430px] overflow-hidden rounded-2xl">

          <MapContainer
            center={position}
            zoom={10}
            scrollWheelZoom={true}
            className="h-full w-full"
          >

            {/* Move map */}

            <MapController
              position={position}
            />


            {/* Location button */}

            <LocationController
              onLocationFound={
                handleMyLocation
              }
            />


            {/* OpenStreetMap */}

            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />


            {/* Marker */}

            <Marker
              position={position}
            >

              <Popup>

                <div className="text-sm">

                  <strong>
                    {locationName}
                  </strong>

                  <br />

                  Weather information

                </div>

              </Popup>

            </Marker>

          </MapContainer>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* Bottom information */}
      {/* -------------------------------- */}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">

        <div className="flex items-center gap-2">

          <span className="flex h-2 w-2 rounded-full bg-emerald-400" />

          Interactive map

        </div>

        <div className="flex items-center gap-2">

          <span>
            Search a location or use your current position
          </span>

        </div>

      </div>

    </section>
  );
}


export default WeatherMap;