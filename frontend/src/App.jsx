import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askWeatherGPT = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setWeather(null);
    setForecast(null);
    setIntelligence(null);
    setAlerts([]);

    const controller = new AbortController();

    // Prevent the frontend from waiting forever.
    const timeout = setTimeout(() => {
      controller.abort();
    }, 60000);

    try {
      const params = new URLSearchParams({
        question: trimmedQuestion,
        session_id: "frontend_user",
      });

      const response = await fetch(
        `${API_URL}/smart-weather?${params.toString()}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
          signal: controller.signal,
        }
      );

      clearTimeout(timeout);

      const rawText = await response.text();

      console.log("Backend status:", response.status);
      console.log("Backend response:", rawText);

      if (!response.ok) {
        throw new Error(
          `Backend returned HTTP ${response.status}`
        );
      }

      let data;

      try {
        data = JSON.parse(rawText);
      } catch {
        // In case the backend ever returns plain text.
        data = rawText;
      }

      console.log("Parsed WeatherGPT data:", data);

      // ----------------------------------------
      // Plain text response
      // ----------------------------------------

      if (typeof data === "string") {
        setAnswer(data);
        return;
      }

      // ----------------------------------------
      // AI answer
      // ----------------------------------------

      if (data.answer) {
        setAnswer(String(data.answer));
      } else if (data.message) {
        setAnswer(String(data.message));
      } else if (data.response) {
        setAnswer(String(data.response));
      } else {
        setAnswer("WeatherGPT received the weather information.");
      }

      // ----------------------------------------
      // Weather data
      // ----------------------------------------

      if (data.weather) {
        setWeather(data.weather);
      }

      // ----------------------------------------
      // Forecast data
      // ----------------------------------------

      if (data.forecast) {
        setForecast(data.forecast);
      }

      // ----------------------------------------
      // Intelligence
      // ----------------------------------------

      if (data.intelligence) {
        setIntelligence(data.intelligence);
      }

      // ----------------------------------------
      // Alerts
      // ----------------------------------------

      if (Array.isArray(data.alerts)) {
        setAlerts(data.alerts);
      }

      // ----------------------------------------
      // Some versions may return alert objects
      // ----------------------------------------

      if (data.alerts && !Array.isArray(data.alerts)) {
        setAlerts([data.alerts]);
      }
    } catch (err) {
      console.error("WeatherGPT request error:", err);

      clearTimeout(timeout);

      if (err.name === "AbortError") {
        setError(
          "The request took too long. Please try again."
        );
      } else if (
        err.message &&
        err.message.includes("Failed to fetch")
      ) {
        setError(
          "Unable to connect to WeatherGPT. Make sure the FastAPI server is running on port 8000."
        );
      } else {
        setError(
          err.message ||
            "Something went wrong while contacting WeatherGPT."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askWeatherGPT();
    }
  };

  const useSuggestion = (text) => {
    setQuestion(text);
    setError("");
  };

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">

        <div className="logo">
          🌦️ WeatherGPT
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Weather Assistant
        </div>

      </header>


      {/* MAIN */}

      <main className="main">

        {/* HERO */}

        <section className="hero">

          <div className="hero-icon">
            🌤️
          </div>

          <h1>
            Your Intelligent
            <br />
            Weather Assistant
          </h1>

          <p>
            Ask anything about weather, forecasts,
            alerts and conditions.
          </p>

        </section>


        {/* CHAT */}

        <section className="chat-card">

          {/* WELCOME */}

          <div className="welcome-message">

            <div className="bot-avatar">
              🌦️
            </div>

            <div className="message">

              <h3>
                Hi! I'm WeatherGPT 👋
              </h3>

              <p>
                Ask me about the weather in any city.
                I can provide current conditions,
                forecasts, recommendations and alerts.
              </p>

            </div>

          </div>


          {/* LOADING */}

          {loading && (

            <div className="answer-message">

              <div className="bot-avatar">
                🤖
              </div>

              <div className="message">

                <h3>
                  WeatherGPT
                </h3>

                <p>
                  Checking the weather...
                </p>

              </div>

            </div>

          )}


          {/* ANSWER */}

          {!loading && answer && (

            <div className="answer-message">

              <div className="bot-avatar">
                🤖
              </div>

              <div className="message answer-content">

                <h3>
                  WeatherGPT
                </h3>

                <p>
                  {answer}
                </p>

              </div>

            </div>

          )}


          {/* WEATHER CARD */}

          {!loading && weather && (

            <div className="data-card">

              <h3>
                🌡️ Current Weather
              </h3>

              <div className="weather-grid">

                {weather.temperature !== undefined && (
                  <div className="weather-item">
                    <span>Temperature</span>
                    <strong>
                      {weather.temperature}°C
                    </strong>
                  </div>
                )}

                {weather.feels_like !== undefined && (
                  <div className="weather-item">
                    <span>Feels like</span>
                    <strong>
                      {weather.feels_like}°C
                    </strong>
                  </div>
                )}

                {weather.humidity !== undefined && (
                  <div className="weather-item">
                    <span>Humidity</span>
                    <strong>
                      {weather.humidity}%
                    </strong>
                  </div>
                )}

                {weather.wind_speed !== undefined && (
                  <div className="weather-item">
                    <span>Wind</span>
                    <strong>
                      {weather.wind_speed}
                    </strong>
                  </div>
                )}

                {weather.weather && (
                  <div className="weather-item">
                    <span>Condition</span>
                    <strong>
                      {weather.weather}
                    </strong>
                  </div>
                )}

              </div>

            </div>

          )}


          {/* INTELLIGENCE */}

          {!loading && intelligence && (

            <div className="data-card">

              <h3>
                🧠 Weather Intelligence
              </h3>

              {intelligence.conditions &&
                intelligence.conditions.length > 0 && (

                  <div className="intelligence-section">

                    <strong>
                      Conditions
                    </strong>

                    <div className="tag-container">

                      {intelligence.conditions.map(
                        (condition, index) => (
                          <span
                            className="tag"
                            key={index}
                          >
                            {condition}
                          </span>
                        )
                      )}

                    </div>

                  </div>

                )}


              {intelligence.severity && (

                <div className="intelligence-section">

                  <strong>
                    Severity
                  </strong>

                  <span className="severity">
                    {intelligence.severity}
                  </span>

                </div>

              )}


              {intelligence.recommendations &&
                intelligence.recommendations.length > 0 && (

                  <div className="intelligence-section">

                    <strong>
                      Recommendations
                    </strong>

                    <ul>

                      {intelligence.recommendations.map(
                        (recommendation, index) => (
                          <li key={index}>
                            {recommendation}
                          </li>
                        )
                      )}

                    </ul>

                  </div>

                )}

            </div>

          )}


          {/* ALERTS */}

          {!loading && alerts.length > 0 && (

            <div className="alert-card">

              <h3>
                ⚠️ Weather Alerts
              </h3>

              {alerts.map((alert, index) => (

                <div
                  className="alert-item"
                  key={index}
                >
                  {typeof alert === "string"
                    ? alert
                    : alert.message ||
                      alert.description ||
                      JSON.stringify(alert)}
                </div>

              ))}

            </div>

          )}


          {/* ERROR */}

          {error && (

            <div className="error-message">

              ⚠️ {error}

            </div>

          )}


          {/* SUGGESTIONS */}

          <div className="suggestions">

            <button
              onClick={() =>
                useSuggestion(
                  "What's the weather in Ahmedabad?"
                )
              }
              disabled={loading}
            >
              🌡️ Current weather
            </button>

            <button
              onClick={() =>
                useSuggestion(
                  "Will it rain tomorrow in Ahmedabad?"
                )
              }
              disabled={loading}
            >
              🌧️ Rain forecast
            </button>

            <button
              onClick={() =>
                useSuggestion(
                  "What will the weather be like this week in Ahmedabad?"
                )
              }
              disabled={loading}
            >
              📅 Weekly forecast
            </button>

            <button
              onClick={() =>
                useSuggestion(
                  "Are there any weather alerts in Ahmedabad?"
                )
              }
              disabled={loading}
            >
              ⚠️ Weather alerts
            </button>

          </div>


          {/* INPUT */}

          <div className="input-area">

            <input
              type="text"
              placeholder="Ask WeatherGPT anything..."
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={askWeatherGPT}
              disabled={
                loading || !question.trim()
              }
              aria-label="Send question"
            >
              {loading ? "..." : "➤"}
            </button>

          </div>


          <div className="input-hint">
            Press Enter to ask WeatherGPT
          </div>

        </section>

      </main>


      {/* FOOTER */}

      <footer>
        WeatherGPT • Intelligent Weather Forecasting & Alerts
      </footer>

    </div>
  );
}

export default App;