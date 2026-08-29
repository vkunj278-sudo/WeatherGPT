import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [alertRequested, setAlertRequested] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatEndRef = useRef(null);

  const askWeatherGPT = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setLoading(true);
    setQuestion("");
    setError("");
    setAnswer("");

    setWeather(null);
    setForecast(null);
    setIntelligence(null);
    setAlerts([]);

    setAlertRequested(
      /alert|warning|danger|storm|thunderstorm/i.test(
        trimmedQuestion
      )
    );

    const controller = new AbortController();

    const timeout = setTimeout(() => {
      controller.abort();
    }, 60000);

    try {
      const params = new URLSearchParams();

      params.set(
        "question",
        trimmedQuestion
      );

      params.set(
        "session_id",
        "frontend_user"
      );

      const response = await fetch(
        `${API_URL}/smart-weather?${params.toString()}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json"
          },
          signal: controller.signal
        }
      );

      clearTimeout(timeout);

      const rawText = await response.text();

      console.log(
        "WeatherGPT HTTP status:",
        response.status
      );

      console.log(
        "WeatherGPT raw response:",
        rawText
      );

      if (!response.ok) {
        let errorMessage =
          `Backend returned HTTP ${response.status}`;

        try {
          const errorData =
            JSON.parse(rawText);

          if (errorData.detail) {
            errorMessage =
              errorData.detail;
          }

          if (errorData.message) {
            errorMessage =
              errorData.message;
          }
        } catch {
          // Keep default message.
        }

        throw new Error(
          errorMessage
        );
      }

      let data;

      try {
        data = JSON.parse(
          rawText
        );
      } catch {
        data = {
          answer: rawText
        };
      }

      console.log(
        "WeatherGPT parsed response:",
        data
      );

      // --------------------------------------------------
      // LOCATION REQUIRED
      // --------------------------------------------------

      if (
        data.status ===
        "need_location"
      ) {
        setAnswer(
          data.message ||
          "Please provide a city or location."
        );

        return;
      }

      // --------------------------------------------------
      // ANSWER
      // --------------------------------------------------

      if (data.answer) {
        const newAnswer = String(data.answer);

        setAnswer(newAnswer);

        setChatHistory((previousHistory) => [
          ...previousHistory,
          {
            question: trimmedQuestion,
            answer: newAnswer,
          },
        ]);
      } else if (data.message) {
        const newAnswer = String(data.message);

        setAnswer(newAnswer);

        setChatHistory((previousHistory) => [
          ...previousHistory,
          {
            question: trimmedQuestion,
            answer: newAnswer,
          },
        ]);
      } else if (data.response) {
        setAnswer(
          String(data.response)
        );
      } else {
        setAnswer(
          "WeatherGPT received the weather information."
        );
      }

      // --------------------------------------------------
      // WEATHER
      // --------------------------------------------------

      if (data.weather) {
        setWeather(
          data.weather
        );
      }

      // --------------------------------------------------
      // FORECAST
      // --------------------------------------------------

      if (data.forecast) {
        setForecast(
          data.forecast
        );
      }

      // --------------------------------------------------
      // INTELLIGENCE
      // --------------------------------------------------

      if (data.intelligence) {
        setIntelligence(
          data.intelligence
        );
      }

      // --------------------------------------------------
      // ALERTS
      // --------------------------------------------------

      if (
        Array.isArray(
          data.alerts
        )
      ) {
        setAlerts(
          data.alerts
        );
      } else if (
        data.alerts
      ) {
        setAlerts([
          data.alerts
        ]);
      }

    } catch (err) {
      console.error(
        "WeatherGPT request error:",
        err
      );

      clearTimeout(timeout);

      if (
        err.name ===
        "AbortError"
      ) {
        setError(
          "The request took too long. Please try again."
        );
      } else if (
        err.message &&
        err.message.includes(
          "Failed to fetch"
        )
      ) {
        setError(
          "The browser could not connect to WeatherGPT. Check that FastAPI is running and CORS is enabled."
        );
      } else {
        setError(
          err.message ||
          "Something went wrong while contacting WeatherGPT."
        );
      }
    } finally {
      setLoading(false);
      setQuestion("");
    }
  };
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [chatHistory, loading, answer]);

  const handleKeyDown = (
    event
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      askWeatherGPT();
    }
  };


  const useSuggestion = (
    text
  ) => {
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
            Ask anything about weather,
            forecasts, alerts and conditions.
          </p>

        </section>


        {/* CHAT CARD */}

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
                Ask me about the weather
                in any city. I can provide
                current conditions, forecasts,
                recommendations and alerts.
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

                <div className="loading-state">
                  <span>Checking the weather</span>
                  <span className="loading-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                  </span>
                </div>

              </div>

            </div>

          )}


          {/* ANSWER */}

          {!loading &&
            answer && (

              <div className="answer-message">

                <div className="bot-avatar">
                  🤖
                </div>

                <div className="message answer-content">

                  <h3>
                    WeatherGPT
                  </h3>

                  <p style={{ whiteSpace: "pre-wrap" }}>
                    {String(answer).replace(/\*\*/g, "")}
                  </p>

                </div>

              </div>

            )}
          {/* CHAT HISTORY */}

          {chatHistory.length > 0 && (

            <div className="chat-history">

              {chatHistory.map((chat, index) => (

                <div
                  className="history-item"
                  key={index}
                >

                  <div className="user-message">

                    <div className="user-avatar">
                      👤
                    </div>

                    <div className="message">

                      <p>
                        {chat.question}
                      </p>

                    </div>

                  </div>


                  <div className="answer-message">

                    <div className="bot-avatar">
                      🤖
                    </div>

                    <div className="message answer-content">

                      <h3>
                        WeatherGPT
                      </h3>

                      <p style={{ whiteSpace: "pre-wrap" }}>
                        {String(chat.answer).replace(/\*\*/g, "")}
                      </p>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          )}

          {/* CURRENT WEATHER */}

          {!loading &&
            weather && (

              <div className="data-card">

                <h3>
                  🌡️ Current Weather
                </h3>

                <div className="weather-grid">

                  {weather.city && (

                    <div className="weather-item">

                      <span>
                        Location
                      </span>

                      <strong>
                        {weather.city}
                        {weather.country
                          ? `, ${weather.country}`
                          : ""}
                      </strong>

                    </div>

                  )}

                  {weather.temperature !==
                    undefined && (

                    <div className="weather-item">

                      <span>
                        Temperature
                      </span>

                      <strong>
                        {weather.temperature}°C
                      </strong>

                    </div>

                  )}

                  {weather.feels_like !==
                    undefined && (

                    <div className="weather-item">

                      <span>
                        Feels like
                      </span>

                      <strong>
                        {weather.feels_like}°C
                      </strong>

                    </div>

                  )}

                  {weather.humidity !==
                    undefined && (

                    <div className="weather-item">

                      <span>
                        Humidity
                      </span>

                      <strong>
                        {weather.humidity}%
                      </strong>

                    </div>

                  )}

                  {weather.wind_speed !==
                    undefined && (

                    <div className="weather-item">

                      <span>
                        Wind
                      </span>

                      <strong>
                        {weather.wind_speed} m/s
                      </strong>

                    </div>

                  )}

                  {weather.weather && (

                    <div className="weather-item">

                      <span>
                        Condition
                      </span>

                      <strong>
                        {weather.weather}
                      </strong>

                    </div>

                  )}

                </div>

              </div>

            )}


          {/* FORECAST */}

          {!loading &&
            forecast &&
            Array.isArray(
              forecast.forecast
            ) &&
            forecast.forecast.length > 0 && (

              <div className="data-card">

                <h3>
                  📅 Forecast
                </h3>

                <div className="forecast-list">

                  {forecast.forecast.map(
                    (item, index) => (

                      <div
                        className="forecast-item"
                        key={
                          `${item.datetime || "forecast"}-${index}`
                        }
                      >

                        <div className="forecast-date">

                          <strong>
                            {item.datetime ||
                              "Forecast"}
                          </strong>

                          {item.weather && (
                            <span>
                              {item.weather}
                            </span>
                          )}

                        </div>

                        <div className="forecast-values">

                          {item.temperature !==
                            undefined && (

                            <span>
                              🌡️{" "}
                              {item.temperature}°C
                            </span>

                          )}

                          {item.feels_like !==
                            undefined && (

                            <span>
                              Feels{" "}
                              {item.feels_like}°C
                            </span>

                          )}

                          {item.humidity !==
                            undefined && (

                            <span>
                              💧{" "}
                              {item.humidity}%
                            </span>

                          )}

                          {item.wind_speed !== undefined && (
                            <span>
                              💨 Wind {item.wind_speed} m/s
                            </span>
                          )}

                          {item.rain_3h !== undefined && (
                            <span>
                              🌧️ Rain {item.rain_3h} mm
                            </span>
                          )}

                        </div>

                      </div>

                    )
                  )}

                </div>

              </div>

            )}


          {/* NO FORECAST */}

          {!loading &&
            forecast &&
            Array.isArray(
              forecast.forecast
            ) &&
            forecast.forecast.length === 0 && (

              <div className="data-card">

                <h3>
                  📅 Forecast
                </h3>

                <p>
                  No forecast entries were
                  available for the requested
                  time period.
                </p>

              </div>

            )}


          {/* INTELLIGENCE */}

          {!loading &&
            intelligence && (

              <div className="data-card">

                <h3>
                  🧠 Weather Intelligence
                </h3>


                {Array.isArray(
                  intelligence.conditions
                ) &&
                  intelligence.conditions.length >
                    0 && (

                    <div className="intelligence-section">

                      <strong>
                        Conditions
                      </strong>

                      <div className="tag-container">

                        {intelligence.conditions.map(
                          (
                            condition,
                            index
                          ) => (

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


                {Array.isArray(
                  intelligence.recommendations
                ) &&
                  intelligence.recommendations.length >
                    0 && (

                    <div className="intelligence-section">

                      <strong>
                        Recommendations
                      </strong>

                      <ul>

                        {intelligence.recommendations.map(
                          (
                            recommendation,
                            index
                          ) => (

                            <li key={index}>
                              {recommendation}
                            </li>

                          )
                        )}

                      </ul>

                    </div>

                  )}


                {Array.isArray(
                  intelligence.warnings
                ) &&
                  intelligence.warnings.length >
                    0 && (

                    <div className="intelligence-section">

                      <strong>
                        Warnings
                      </strong>

                      <ul>

                        {intelligence.warnings.map(
                          (
                            warning,
                            index
                          ) => (

                            <li key={index}>
                              {warning}
                            </li>

                          )
                        )}

                      </ul>

                    </div>

                  )}

              </div>

            )}


          {/* ALERTS */}

          {!loading &&
            (alerts.length > 0 || alertRequested) && (

              <div className="alert-card">

                <h3>
                  ⚠️ Weather Alerts
                </h3>

                {alerts.length > 0 ? (

                  alerts.map(
                    (
                      alert,
                      index
                    ) => (

                      <div
                        className="alert-item"
                        key={index}
                      >

                        {typeof alert ===
                        "string"
                          ? alert
                          : alert.warning ||
                            alert.message ||
                            alert.description ||
                            JSON.stringify(
                              alert
                            )}

                      </div>

                    )
                  )

                ) : (

                  <div className="alert-item">
                    No active weather alerts for this location.
                  </div>

                )}

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
                setQuestion(
                  event.target.value
                )
              }
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={askWeatherGPT}
              disabled={
                loading ||
                !question.trim()
              }
              aria-label="Send question"
            >
              {loading
                ? "..."
                : "➤"}
            </button>

          </div>


          <div className="input-hint">
            Press Enter to ask WeatherGPT
          </div>
          <div ref={chatEndRef} />

        </section>

      </main>


      {/* FOOTER */}

      <footer>
        WeatherGPT • Intelligent
        Weather Forecasting & Alerts
      </footer>

    </div>
  );
}

export default App;