import React, { useState, useEffect } from "react";
import "./index";
import InputForm from "./components/InputForm.jsx";

function App() {
  const [studyGuide, setStudyGuide] = useState(""); // Holds the final text
  const [displayedText, setDisplayedText] = useState(""); // Holds the "typed" text

  const handleStudyGuideGenerated = (generatedText) => {
    setStudyGuide(generatedText); // Set the final text
    setDisplayedText(""); // Reset the typing display
  };

  // Typing simulation effect
  useEffect(() => {
    if (studyGuide) {
      let index = 0;
      const interval = setInterval(() => {
        if (index < studyGuide.length) {
          setDisplayedText((prev) => prev + studyGuide[index]);
          index++;
        } else {
          clearInterval(interval);
        }
      }, 2); // Adjust typing speed here (50ms per character)
      return () => clearInterval(interval);
    }
  }, [studyGuide]);

  return (
    <div className="app">
      <nav className="navbar">
        <h1>TooturAI</h1>
      </nav>

      <div className="content">
        <div className="output-area">
          {studyGuide ? (
            <div className="study-guide">
              <h2>Generated Study Guide</h2>
              <p>{displayedText}</p> {/* Display the "typed" text */}
            </div>
          ) : (
            <>
              <h1>Got an exam coming up?</h1>
              <h2>Enter a topic to generate a study guide.</h2>
            </>
          )}
        </div>
        <InputForm onStudyGuideGenerated={handleStudyGuideGenerated} />
      </div>
    </div>
  );
}

export default App;
