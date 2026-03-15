import { useState } from "react";

interface RoleToggleProps {
  value: "recruiter" | "candidate";
  onChange: (role: "recruiter" | "candidate") => void;
}

const RoleToggle = ({ value, onChange }: RoleToggleProps) => (
  <div className="flex items-center bg-muted rounded-full p-1 mb-6">
    <button
      onClick={() => onChange("recruiter")}
      className={`flex-1 text-sm font-medium py-2 px-4 rounded-full transition-all duration-200 ${
        value === "recruiter"
          ? "bg-surface text-foreground shadow-card"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      I am a Recruiter
    </button>
    <button
      onClick={() => onChange("candidate")}
      className={`flex-1 text-sm font-medium py-2 px-4 rounded-full transition-all duration-200 ${
        value === "candidate"
          ? "bg-surface text-foreground shadow-card"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      I am a Candidate
    </button>
  </div>
);

export default RoleToggle;
