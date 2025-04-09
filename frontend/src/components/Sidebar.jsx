
// import React, { useEffect, useState } from "react";
// import "./Sidebar.css";

// function Sidebar({ onNavigate, onSelectHistory, onLogout, user, currentPage, setSelectedStudyGuide, history }) {
//   const [studyGuides, setStudyGuides] = useState([]);

//   useEffect(() => {
//     if (user) {
//       fetch(`http://localhost:8000/api/get-study-guides?email=${user.email}`)
//         .then((response) => response.json())
//         .then((data) => {
//           setStudyGuides(data.study_guides || []);
//         })
//         .catch((error) => console.error("Error fetching study guides:", error));
//     }
//   }, [user, history]); 

//   return (
//     <div className="sidebar">
//       <ul className="nav-links-side">
//         <li onClick={() => onNavigate("home")}>Home</li>
//         <li onClick={() => {
//     onSelectHistory(null); // Reset previous study guide
//     onNavigate("studyGuide");
// }}>
//   New Study Guide
// </li>

        

//         <li onClick={() => onNavigate("flashcards")}>Flashcards</li>
//         <li onClick={() => onNavigate("studyPlan")}>Study Plan</li>
//         <li onClick={() => onNavigate("practiceTests")}>Practice Tests</li>
//         <li className="logout" onClick={onLogout}>Logout</li>
//         {/* Display past study guides */}
//         {studyGuides.length > 0 && currentPage === "studyGuide"&& (
//           <div className="history-section">
//             <h3 className="history-title"></h3>
//             <ul className="history-list">
//               {studyGuides.map((guide) => (
//                 <li key={guide._id} onClick={() => {
//                     if (!guide.conversation || guide.conversation.length === 0) {
//                       guide.conversation = [
//                         { user_prompt: guide.title, response: guide.content }
//                       ];
//                     }
//                     onSelectHistory(guide);
//                   }}>
//                     {guide.title}
//                   </li>
//               ))}
//             </ul>
//           </div>
//         )}
//       </ul>
//     </div>
//   );
// }

// export default Sidebar;

import React, { useEffect, useState, useRef } from "react";
import "./Sidebar.css";

function Sidebar({ onNavigate, onSelectHistory, onLogout, user, currentPage, setSelectedStudyGuide, history, isSidebarOpen, setIsSidebarOpen }) {
  const [studyGuides, setStudyGuides] = useState([]);
  const [menuVisible, setMenuVisible] = useState(null); // Track which guide has options open
  const [editMode, setEditMode] = useState(null); // Track renaming state
  const [newTitle, setNewTitle] = useState(""); // Store new title input
  const menuRef = useRef(null); // Reference for detecting outside clicks

  // Fetch user's study guides from the backend
  useEffect(() => {
    if (user) {
      fetch(`http://localhost:8000/api/get-study-guides?email=${user.email}`)
        .then((response) => response.json())
        .then((data) => {
          setStudyGuides(data.study_guides || []);
        })
        .catch((error) => console.error("Error fetching study guides:", error));
    }
  }, [user, history]);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuVisible(null); // Close menu if clicking outside
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Handle renaming a study guide
  const handleRename = async (studyGuideId) => {
    if (!newTitle.trim()) return;

    try {
      const response = await fetch("http://localhost:8000/api/rename-study-guide", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: user.email,
          study_guide_id: studyGuideId,
          new_title: newTitle,
        }),
      });

      if (response.ok) {
        setStudyGuides((prevGuides) =>
          prevGuides.map((guide) =>
            guide._id === studyGuideId ? { ...guide, title: newTitle } : guide
          )
        );
        setEditMode(null);
        setNewTitle("");
        setMenuVisible(null);
      } else {
        console.error("Failed to rename study guide.");
      }
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  // Handle deleting a study guide
  const handleDelete = async (studyGuideId) => {
    try {
      const response = await fetch("http://localhost:8000/api/delete-study-guide", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: user.email,
          study_guide_id: studyGuideId,
        }),
      });

      if (response.ok) {
        setStudyGuides((prevGuides) =>
          prevGuides.filter((guide) => guide._id !== studyGuideId)
        );
        setMenuVisible(null); // Close menu after deleting
      } else {
        console.error("Failed to delete study guide.");
      }
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  return (
    <div className={`sidebar ${!isSidebarOpen ? "closed" : ""}`}> {/* Fix className */}
      <button className="sidebar-toggle" onClick={() => setIsSidebarOpen((prev) => !prev)}>
        ☰
      </button>
      <ul className="nav-links-side">
        <li onClick={() => onNavigate("home")}>Home</li>
        <li
          onClick={() => {
            onSelectHistory(null);
            onNavigate("studyGuide");
          }}
        >
          New Study Guide
        </li>

        <li onClick={() => onNavigate("flashcards")}>Flashcards</li>
        <li onClick={() => onNavigate("studyPlan")}>Study Plan</li>
        <li onClick={() => onNavigate("practiceTests")}>Practice Tests</li>
        <li className="logout" onClick={onLogout}>
          Logout
        </li>

        {/* Display past study guides with delete & rename options */}
        {studyGuides.length > 0 && currentPage === "studyGuide" && (
          <div className="history-section">
            <h3 className="history-title">Activity</h3>
            <ul className="history-list">
              {studyGuides.map((guide) => (
                <li key={guide._id} className="history-item">
                  {/* Study Guide Button */}
                  <div className="study-guide-container">
                    {/* Click to Open Study Guide */}
                    {editMode === guide._id ? (
                      <input
                        type="text"
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        onBlur={() => handleRename(guide._id)}
                        onKeyDown={(e) => e.key === "Enter" && handleRename(guide._id)}
                        className="rename-input"
                        autoFocus
                      />
                    ) : (
                      <span onClick={() => onSelectHistory(guide)}>{guide.title}</span>
                    )}

                    {/* Three-dot menu button */}
                    <button
                      className="menu-button"
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent study guide from being selected when clicking menu
                        setMenuVisible(menuVisible === guide._id ? null : guide._id);
                      }}
                    >
                      ⋮
                    </button>
                  </div>

                  {/* Show Rename & Delete only when three-dot menu is clicked */}
                  {menuVisible === guide._id && (
                    <div className="dropdown-menu" ref={menuRef}>
                      <span onClick={() => setEditMode(guide._id)}>✏ Rename</span>
                      <span onClick={() => handleDelete(guide._id)}>🗑 Delete</span>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </ul>
    </div>
  );
}

export default Sidebar;


