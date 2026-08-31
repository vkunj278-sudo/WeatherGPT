import { useEffect, useMemo, useState } from "react";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Thermometer,
  CloudRain,
  Droplets,
  Wind,
  Umbrella,
  RefreshCcw,
  CalendarDays,
  Clock3,
  AlertTriangle,
  MapPin,
} from "lucide-react";

// Local development uses the FastAPI server directly.
// Production uses the Vercel /api route so the browser never tries to call localhost.
const API_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "/api");

function ChatBox({ locationName = "Selected Location", temperatureUnit = "C" }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [online, setOnline] = useState(true);

  const sessionId = useMemo(() => {
    const key = "weathergpt_session_id";
    let id = localStorage.getItem(key);
    if (!id) {
      id = `web_${crypto.randomUUID ? crypto.randomUUID() : Date.now()}`;
      localStorage.setItem(key, id);
    }
    return id;
  }, []);

  const quickQuestions = [
    ["Temperature", "What is the current temperature?", Thermometer],
    ["Rain", "Is it raining?", CloudRain],
    ["Next 3 hours", "Will it rain in the next 3 hours?", Clock3],
    ["Tonight", "What will the weather be like tonight?", Sparkles],
    ["Tomorrow", "What will the weather be like tomorrow?", CalendarDays],
    ["Humidity", "What is the humidity?", Droplets],
    ["Wind", "What is the wind speed?", Wind],
    ["Umbrella", "Should I carry an umbrella later?", Umbrella],
  ];

  const greeting = `Hello! I'm WeatherGPT. Ask me anything about current or upcoming weather in ${locationName}.`;

  useEffect(() => {
    setMessages([{ sender: "bot", text: greeting }]);
    setMessage("");
  }, [locationName]); // eslint-disable-line react-hooks/exhaustive-deps

  const formatAnswer = (text) => {
    if (!text) return "I couldn't generate a weather response.";
    return text
      .replace(/\*\*(.*?)\*\*/g, "$1")
      .replace(/^#+\s*/gm, "")
      .trim();
  };

  const askBackend = async (question) => {
    // The selected map location becomes the implicit location for follow-up questions.
    const lower = question.toLowerCase();
    const hasLocation = /\b(?:in|at|for|near)\s+(?:the\s+)?[a-z][a-z .'-]+/i.test(question);
    const hasKnownLocation = [
      "ahmedabad", "surat", "mumbai", "delhi", "new delhi", "bengaluru",
      "bangalore", "chennai", "hyderabad", "pune", "kolkata", "vadodara",
      "rajkot", "jaipur", "lucknow", "indore", "bhavnagar",
    ].some((city) => lower.includes(city));

    const finalQuestion = hasLocation || hasKnownLocation
      ? question
      : `${question} in ${locationName}`;

    const apiPath = `${API_URL.replace(/\\/$/, "")}/smart-weather`;

    // `new URL()` needs an absolute base in the browser. In production
    // `/api` is intentionally relative so it works on any Vercel domain.
    const url = apiPath.startsWith("http")
      ? new URL(apiPath)
      : new URL(apiPath, window.location.origin);
    url.searchParams.set("question", finalQuestion);
    url.searchParams.set("session_id", sessionId);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);

    try {
      const response = await fetch(url.toString(), { signal: controller.signal });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Weather service returned an error.");
      }

      if (data.status === "need_location") {
        return { text: data.message || "Which city would you like me to check?" };
      }

      if (data.status === "error") {
        throw new Error(data.message || "Unable to process the weather request.");
      }

      setOnline(true);
      return {
        text: formatAnswer(data.answer),
        data,
      };
    } catch (error) {
      setOnline(false);
      if (error.name === "AbortError") {
        throw new Error("The weather service took too long to respond. Please try again.");
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  };

  const handleSend = async (questionText = null) => {
    const userQuestion = (questionText ?? message).trim();
    if (!userQuestion || loading) return;

    setMessages((prev) => [...prev, { sender: "user", text: userQuestion }]);
    setMessage("");
    setLoading(true);

    try {
      const result = await askBackend(userQuestion);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: result.text,
          data: result.data,
        },
      ]);
    } catch (error) {
      console.error("WeatherGPT chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: `I couldn't connect to the WeatherGPT service. ${error.message || "Please try again."}`,
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([{ sender: "bot", text: greeting }]);
    setMessage("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const temperature = (value) => {
    if (value == null) return null;
    const n = Number(value);
    return temperatureUnit === "F" ? Math.round((n * 9) / 5 + 32) : Math.round(n);
  };

  return (
    <section id="chat" className="mt-24 scroll-mt-28">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-300">
              <Sparkles size={16} />
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">AI Assistant</span>
          </div>
          <h2 className="text-3xl font-semibold tracking-tight text-white">Ask WeatherGPT</h2>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            Get weather-aware answers for <span className="font-medium text-slate-200">{locationName}</span>
          </p>
        </div>

        <button
          type="button"
          onClick={resetChat}
          disabled={loading}
          className="inline-flex w-fit items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-xs font-medium text-slate-400 transition hover:border-cyan-400/20 hover:bg-cyan-400/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          <RefreshCcw size={14} /> New chat
        </button>
      </div>

      <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/60 shadow-2xl shadow-black/20 backdrop-blur-xl">
        <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4 sm:px-7">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 shadow-lg shadow-cyan-500/10">
              <Bot size={18} />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">WeatherGPT</p>
              <div className="mt-0.5 flex items-center gap-2">
                <span className={`h-1.5 w-1.5 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"}`} />
                <span className="text-[11px] text-slate-500">{online ? "Live weather connected" : "Connection issue"}</span>
              </div>
            </div>
          </div>
          <div className={`hidden rounded-full border px-3 py-1.5 sm:block ${online ? "border-emerald-400/15 bg-emerald-400/5" : "border-amber-400/15 bg-amber-400/5"}`}>
            <span className={`text-[10px] font-semibold uppercase tracking-wider ${online ? "text-emerald-300" : "text-amber-300"}`}>
              {online ? "Online" : "Retry"}
            </span>
          </div>
        </div>

        <div className="min-h-[320px] max-h-[520px] overflow-y-auto px-5 py-7 sm:px-7 sm:py-8">
          <div className="space-y-6">
            {messages.map((chatMessage, index) => {
              const isUser = chatMessage.sender === "user";
              const weather = chatMessage.data?.weather;
              const intelligence = chatMessage.data?.intelligence;

              return (
                <div key={`${index}-${chatMessage.text}`} className={`flex items-start gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
                  {!isUser && (
                    <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-blue-600">
                      <Bot size={16} />
                    </div>
                  )}

                  <div className="max-w-[88%] sm:max-w-[76%]">
                    <div className={`rounded-2xl px-4 py-3 text-sm leading-6 ${isUser ? "rounded-br-md bg-cyan-400 text-slate-950" : chatMessage.error ? "rounded-bl-md border border-rose-400/20 bg-rose-400/5 text-rose-200" : "rounded-bl-md border border-white/[0.07] bg-slate-800/70 text-slate-200"}`}>
                      {chatMessage.text}
                    </div>

                    {!isUser && weather && (
                      <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-slate-400">
                        {weather.temperature != null && <span className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1"><Thermometer size={12} className="mr-1 inline" />{temperature(weather.temperature)}°{temperatureUnit}</span>}
                        {weather.humidity != null && <span className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1"><Droplets size={12} className="mr-1 inline" />{weather.humidity}% humidity</span>}
                        {weather.wind_speed != null && <span className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1"><Wind size={12} className="mr-1 inline" />{Math.round(weather.wind_speed)} m/s</span>}
                        {chatMessage.data?.detected_city && <span className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1"><MapPin size={12} className="mr-1 inline" />{chatMessage.data.detected_city}</span>}
                      </div>
                    )}

                    {!isUser && intelligence?.warnings?.length > 0 && (
                      <div className="mt-2 rounded-xl border border-amber-400/15 bg-amber-400/5 px-3 py-2 text-xs text-amber-200">
                        <AlertTriangle size={13} className="mr-1 inline" />
                        {intelligence.warnings[0]}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-slate-800 text-slate-300">
                      <User size={16} />
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-blue-600"><Bot size={16} /></div>
                <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-white/[0.07] bg-slate-800/70 px-5 py-4">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:-.2s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:-.1s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300" />
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-white/[0.06] px-5 py-4 sm:px-7">
          <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
            {quickQuestions.map(([label, question, Icon]) => (
              <button
                key={label}
                type="button"
                disabled={loading}
                onClick={() => handleSend(question)}
                className="inline-flex flex-shrink-0 items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.025] px-3 py-2 text-[11px] font-medium text-slate-400 transition hover:border-cyan-400/20 hover:bg-cyan-400/5 hover:text-cyan-200 disabled:opacity-50"
              >
                <Icon size={13} /> {label}
              </button>
            ))}
          </div>

          <div className="flex items-end gap-2 rounded-2xl border border-white/10 bg-slate-950/60 p-2 transition focus-within:border-cyan-400/30 focus-within:ring-4 focus-within:ring-cyan-400/5">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder={`Ask about ${locationName}...`}
              className="max-h-32 min-h-11 flex-1 resize-none bg-transparent px-3 py-2.5 text-sm text-white outline-none placeholder:text-slate-600"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => handleSend()}
              disabled={!message.trim() || loading}
              className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/10 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-30"
              title="Send message"
            >
              <Send size={17} />
            </button>
          </div>
          <p className="mt-2 text-center text-[10px] text-slate-600">Enter to send · WeatherGPT uses live weather data</p>
        </div>
      </div>
    </section>
  );
}

export default ChatBox;
