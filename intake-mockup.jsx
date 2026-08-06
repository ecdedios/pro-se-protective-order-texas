import { useState } from "react";

const QUESTIONS = [
  {
    id: "relationship",
    label: "What is your relationship to this person?",
    hint: "This helps us guide you to the right form.",
    type: "choice",
    options: [
      "Spouse or former spouse",
      "Someone I dated",
      "A family member",
      "Someone I live with",
      "Other",
    ],
  },
  {
    id: "county",
    label: "What county do you currently live in?",
    hint: "We'll show filing steps specific to your county.",
    type: "text",
    placeholder: "e.g. Travis County",
  },
  {
    id: "children",
    label: "Do you have children with this person?",
    hint: null,
    type: "choice",
    options: ["Yes", "No"],
  },
  {
    id: "incident",
    label: "In your own words, what happened most recently?",
    hint: "Take your time. There's no wrong way to answer this.",
    type: "textarea",
    placeholder: "Start whenever you're ready...",
  },
];

const NEUTRAL_EXIT_URL = "https://www.weather.gov";

export default function IntakeMockup() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [textDraft, setTextDraft] = useState("");

  const question = QUESTIONS[step];
  const isLast = step === QUESTIONS.length - 1;
  const isFirst = step === 0;

  function commitAndAdvance(value) {
    setAnswers((a) => ({ ...a, [question.id]: value }));
    setTextDraft("");
    if (!isLast) setStep((s) => s + 1);
  }

  function goBack() {
    if (!isFirst) setStep((s) => s - 1);
  }

  function handleExit() {
    setAnswers({});
    window.location.href = NEUTRAL_EXIT_URL;
  }

  return (
    <div
      className="min-h-screen w-full flex flex-col"
      style={{ backgroundColor: "#F7F4EF", color: "#3A3733" }}
    >
      {/* Top bar: quiet, unbranded, quick-exit reads as ordinary navigation */}
      <header className="flex items-center justify-between px-4 py-3 sm:px-6">
        <span className="text-sm tracking-wide" style={{ color: "#7A756B" }}>
          Getting Started
        </span>
        <button
          onClick={handleExit}
          className="text-sm underline decoration-1 underline-offset-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 rounded"
          style={{ color: "#7A756B" }}
        >
          Leave this page
        </button>
      </header>

      {/* Quiet progress trail, not a counter */}
      <div className="flex justify-center gap-1.5 pt-2 pb-6 sm:pb-10">
        {QUESTIONS.map((q, i) => (
          <span
            key={q.id}
            className="h-1.5 w-1.5 rounded-full transition-colors"
            style={{
              backgroundColor: i <= step ? "#6B8F71" : "#E4DFD3",
            }}
          />
        ))}
      </div>

      {/* Question card */}
      <main className="flex-1 flex items-start sm:items-center justify-center px-4 sm:px-6">
        <div
          className="w-full max-w-md rounded-2xl px-5 py-7 sm:px-8 sm:py-10"
          style={{ backgroundColor: "#FFFFFF", border: "1px solid #E4DFD3" }}
        >
          <h1
            className="text-xl sm:text-2xl leading-snug mb-2"
            style={{ fontFamily: "Lora, Georgia, serif", color: "#302C28" }}
          >
            {question.label}
          </h1>
          {question.hint && (
            <p className="text-sm mb-6" style={{ color: "#8A8478" }}>
              {question.hint}
            </p>
          )}

          {question.type === "choice" && (
            <div className="flex flex-col gap-2.5 mt-2">
              {question.options.map((opt) => (
                <button
                  key={opt}
                  onClick={() => commitAndAdvance(opt)}
                  className="text-left w-full rounded-xl px-4 py-3.5 text-base transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
                  style={{
                    backgroundColor:
                      answers[question.id] === opt ? "#EDF2EC" : "#FAF8F4",
                    border: `1px solid ${
                      answers[question.id] === opt ? "#6B8F71" : "#E4DFD3"
                    }`,
                    color: "#3A3733",
                  }}
                >
                  {opt}
                </button>
              ))}
            </div>
          )}

          {question.type === "text" && (
            <input
              type="text"
              value={textDraft}
              onChange={(e) => setTextDraft(e.target.value)}
              placeholder={question.placeholder}
              className="w-full rounded-xl px-4 py-3.5 text-base focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
              style={{
                backgroundColor: "#FAF8F4",
                border: "1px solid #E4DFD3",
                color: "#3A3733",
              }}
            />
          )}

          {question.type === "textarea" && (
            <textarea
              value={textDraft}
              onChange={(e) => setTextDraft(e.target.value)}
              placeholder={question.placeholder}
              rows={5}
              className="w-full rounded-xl px-4 py-3.5 text-base resize-none focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
              style={{
                backgroundColor: "#FAF8F4",
                border: "1px solid #E4DFD3",
                color: "#3A3733",
              }}
            />
          )}

          {(question.type === "text" || question.type === "textarea") && (
            <div className="flex items-center justify-between mt-6">
              <button
                onClick={goBack}
                disabled={isFirst}
                className="text-sm px-2 py-2 rounded disabled:opacity-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
                style={{ color: "#8A8478" }}
              >
                Back
              </button>
              <button
                onClick={() => commitAndAdvance(textDraft)}
                disabled={!textDraft.trim()}
                className="rounded-xl px-6 py-3 text-base font-medium disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
                style={{ backgroundColor: "#6B8F71", color: "#FFFFFF" }}
              >
                {isLast ? "Finish" : "Continue"}
              </button>
            </div>
          )}

          {question.type === "choice" && !isFirst && (
            <button
              onClick={goBack}
              className="text-sm mt-6 px-2 py-2 rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
              style={{ color: "#8A8478" }}
            >
              Back
            </button>
          )}
        </div>
      </main>

      <footer className="px-4 py-5 text-center sm:px-6">
        <p className="text-xs" style={{ color: "#A39D8F" }}>
          Your answers stay on this device and are cleared when you leave.
        </p>
      </footer>
    </div>
  );
}
