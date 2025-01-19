import React, { useState } from "react";
import "./InputForm.css";

function InputForm({ onStudyGuideGenerated }) {
  const [topic, setTopic] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:8000/generate-guide", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_prompt: topic }),
      });

      if (response.ok) {
        const data = await response.json();
        onStudyGuideGenerated(data.study_guide);
      } else {
        setError("Failed to generate study guide. Please try again.");
      }
    } catch (err) {
      setError("Error communicating with the backend.");
      console.error(err);
    }
  };

  return (
    <form className="prompt-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter a topic..."
        required
      />
      <button type="submit">Generate</button>
      {error && <p className="error-message">{error}</p>}
    </form>
  );
}

export default InputForm;
