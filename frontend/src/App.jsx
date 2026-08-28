import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");

  return (
    <div className="app">

      <header className="header">
        <div className="logo">
          🌦️ WeatherGPT
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Weather Assistant
        </div>
      </header>


      <main className="main">

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


        <section className="chat-card">

          <div className="welcome-message">

            <div className="bot-avatar">
              🌦️
            </div>

            <div className="message">

              <h3>Hi! I'm WeatherGPT 👋</h3>

              <p>
                Ask me about the weather in any city.
                I can provide current conditions,
                forecasts, recommendations and alerts.
              </p>

            </div>

          </div>


          <div className="suggestions">

            <button
              onClick={() =>
                setQuestion("What's the weather in Ahmedabad?")
              }
            >
              🌡️ Current weather
            </button>

            <button
              onClick={() =>
                setQuestion("Will it rain tomorrow in Ahmedabad?")
              }
            >
              🌧️ Rain forecast
            </button>

            <button
              onClick={() =>
                setQuestion("What will the weather be like this week in Ahmedabad?")
              }
            >
              📅 Weekly forecast
            </button>

            <button
              onClick={() =>
                setQuestion("Are there any weather alerts in Ahmedabad?")
              }
            >
              ⚠️ Weather alerts
            </button>

          </div>


          <div className="input-area">

            <input
              type="text"
              placeholder="Ask WeatherGPT anything..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />

            <button className="send-button">
              ➤
            </button>

          </div>

        </section>

      </main>


      <footer>
        WeatherGPT • Intelligent Weather Forecasting & Alerts
      </footer>

    </div>
  );
}

export default App;