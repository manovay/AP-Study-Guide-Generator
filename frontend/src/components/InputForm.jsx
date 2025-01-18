import React, { useState } from "react";

function InputForm() {
  const [topic, setTopic] = useState("");
  const [studyGuide, setStudyGuide] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Reset error message

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
        setStudyGuide(data.study_guide);
      } else {
        setError("Failed to generate study guide. Please try again.");
      }
    } catch (err) {
      setError("Error communicating with the backend.");
      console.error(err);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic"
          required
        />
        <button type="submit">Generate</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {studyGuide && (
        <div>
          <h2>Generated Study Guide</h2>
          <p>{studyGuide}</p>
        </div>
      )}
    </div>
  );
}

export default InputForm;
