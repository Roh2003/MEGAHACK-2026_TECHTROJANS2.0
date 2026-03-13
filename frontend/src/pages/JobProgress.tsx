import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

import {
  CheckCircle2,
  Clock,
  Circle,
  FileText,
  Video,
  Users,
  Mic,
  Building2,
  Plus,
  ArrowLeft,
  Check,
  X,
  User,
} from "lucide-react";

type RoundStatus = "completed" | "in-progress" | "upcoming" | "not-set";

interface RoundCandidate {
  name: string;
  score: number;
  status: "passed" | "failed" | "pending";
}

interface Round {
  id: number;
  name: string;
  type: string;
  status: RoundStatus;
  date?: string;
  candidates?: RoundCandidate[];
}

const jobsData: Record<string, { title: string; dept: string; location: string }> = {
  "1": { title: "Senior React Developer", dept: "Engineering", location: "Bangalore" },
  "2": { title: "Product Designer", dept: "Design", location: "Remote" },
  "3": { title: "DevOps Engineer", dept: "Infrastructure", location: "Hyderabad" },
  "4": { title: "Data Scientist", dept: "Analytics", location: "Mumbai" },
  "5": { title: "Frontend Intern", dept: "Engineering", location: "Remote" },
};

const mockRounds: Record<string, Round[]> = {
  "1": [
    { id: 1, name: "Job Posted", type: "posting", status: "completed", date: "Mar 1, 2026" },
    {
      id: 2, name: "AI Screening", type: "ai-screening", status: "completed", date: "Mar 4, 2026",
      candidates: [
        { name: "Arjun Mehta", score: 94, status: "passed" },
        { name: "Priya Sharma", score: 88, status: "passed" },
        { name: "Rahul Verma", score: 85, status: "passed" },
        { name: "Sneha Patel", score: 72, status: "passed" },
        { name: "Vikram Singh", score: 61, status: "failed" },
        { name: "Ananya Rao", score: 45, status: "failed" },
      ],
    },
    {
      id: 3, name: "Assessment", type: "assessment", status: "in-progress", date: "Mar 8, 2026",
      candidates: [
        { name: "Arjun Mehta", score: 91, status: "passed" },
        { name: "Priya Sharma", score: 87, status: "passed" },
        { name: "Rahul Verma", score: 78, status: "pending" },
        { name: "Sneha Patel", score: 0, status: "pending" },
      ],
    },
    { id: 4, name: "Next Round", type: "not-set", status: "not-set" },
  ],
  "3": [
    { id: 1, name: "Job Posted", type: "posting", status: "completed", date: "Mar 2, 2026" },
    {
      id: 2, name: "AI Screening", type: "ai-screening", status: "in-progress", date: "Mar 6, 2026",
      candidates: [
        { name: "Karan Joshi", score: 92, status: "passed" },
        { name: "Meera Nair", score: 79, status: "pending" },
        { name: "Amit Das", score: 65, status: "pending" },
      ],
    },
    { id: 3, name: "Next Round", type: "not-set", status: "not-set" },
  ],
  "4": [
    { id: 1, name: "Job Posted", type: "posting", status: "completed", date: "Mar 3, 2026" },
    { id: 2, name: "AI Screening", type: "ai-screening", status: "upcoming", date: "Mar 10, 2026" },
  ],
  "5": [
    { id: 1, name: "Job Posted", type: "posting", status: "completed", date: "Mar 4, 2026" },
    {
      id: 2, name: "AI Screening", type: "ai-screening", status: "completed", date: "Mar 7, 2026",
      candidates: [
        { name: "Divya Kapoor", score: 96, status: "passed" },
        { name: "Nikhil Gupta", score: 90, status: "passed" },
        { name: "Pooja Reddy", score: 82, status: "passed" },
      ],
    },
    { id: 3, name: "Next Round", type: "not-set", status: "not-set" },
  ],
};

const nextRoundOptions = [
  { icon: FileText, label: "Assessment Exam", description: "Aptitude or technical MCQ test" },
  { icon: Mic, label: "AI Interview", description: "AI-powered voice interview round" },
  { icon: Video, label: "Online Interview", description: "Video call with recruiter/panel" },
  { icon: Building2, label: "In-Person Interview", description: "On-site office interview" },
  { icon: Users, label: "Group Discussion", description: "Panel or group evaluation round" },
];

const statusIcon = (status: RoundStatus, size = "h-4 w-4") => {
  switch (status) {
    case "completed": return <CheckCircle2 className={`${size} text-success shrink-0`} />;
    case "in-progress": return <Clock className={`${size} text-primary shrink-0`} />;
    case "upcoming": return <Circle className={`${size} text-muted-foreground/40 shrink-0`} />;
    case "not-set": return <Plus className={`${size} text-muted-foreground/40 shrink-0`} />;
  }
};

const statusBadge = (status: RoundStatus) => {
  switch (status) {
    case "completed": return <Badge className="bg-success/10 text-success border-0">Completed</Badge>;
    case "in-progress": return <Badge className="bg-primary/10 text-primary border-0">In Progress</Badge>;
    case "upcoming": return <Badge variant="secondary">Upcoming</Badge>;
    default: return <Badge variant="outline">Not Set</Badge>;
  }
};

const candidateStatusStyle = (status: string) => {
  if (status === "passed") return "bg-success/10 border-success/20 text-success";
  if (status === "failed") return "bg-destructive/10 border-destructive/20 text-destructive";
  return "bg-muted/50 border-border/40 text-muted-foreground";
};

const candidateStatusIcon = (status: string) => {
  if (status === "passed") return <Check className="h-4 w-4 text-success" />;
  if (status === "failed") return <X className="h-4 w-4 text-destructive" />;
  return <Clock className="h-4 w-4 text-muted-foreground" />;
};

export default function JobProgress() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<string>("1");

  const job = jobId ? jobsData[jobId] : null;
  const rounds = jobId ? (mockRounds[jobId] || [
    { id: 1, name: "Job Posted", type: "posting", status: "completed" as RoundStatus, date: "Recently" },
    { id: 2, name: "AI Screening", type: "ai-screening", status: "upcoming" as RoundStatus },
  ]) : [];

  if (!job) {
    return (
      <DashboardLayout title="Not Found">
        <p className="text-muted-foreground">Job post not found.</p>
      </DashboardLayout>
    );
  }

  const currentRound = rounds.find(r => r.id.toString() === activeTab);
  const isNotSet = currentRound?.status === "not-set";

  return (
    <DashboardLayout title="Recruitment Progress">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-start gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate("/jobs")} className="shrink-0 mt-0.5">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="font-display text-2xl font-bold text-foreground">{job.title}</h2>
            <p className="text-sm text-muted-foreground mt-1">{job.dept} · {job.location}</p>
          </div>
        </div>

        {/* Vertical Timeline + Content Side-by-Side */}
        <div className="flex gap-6">
          {/* Left: Vertical Timeline Steps */}
          <div className="w-64 shrink-0">
            {rounds.map((round, index) => (
              <div key={round.id} className="relative flex gap-3">
                {/* Icon + Progress Line Column */}
                <div className="flex flex-col items-center shrink-0">
                  {/* Status Icon with Background */}
                  <button
                    onClick={() => setActiveTab(round.id.toString())}
                    className={`flex items-center justify-center w-10 h-10 rounded-full transition-all shrink-0 ${
                      round.status === "completed"
                        ? "bg-success/10 border-2 border-success"
                        : round.status === "in-progress"
                        ? "bg-primary/10 border-2 border-primary"
                        : activeTab === round.id.toString()
                        ? "bg-muted border-2 border-primary/50"
                        : "bg-muted/50 border-2 border-border"
                    }`}
                  >
                    {round.status === "completed" ? (
                      <CheckCircle2 className="h-5 w-5 text-success" />
                    ) : round.status === "in-progress" ? (
                      <Clock className="h-5 w-5 text-primary" />
                    ) : (
                      <Circle className={`h-5 w-5 ${activeTab === round.id.toString() ? "text-primary" : "text-muted-foreground/40"}`} />
                    )}
                  </button>
                  {/* Connecting Line */}
                  {index < rounds.length - 1 && (
                    <div className={`w-0.5 flex-1 min-h-[32px] mt-1 rounded-full ${
                      round.status === "completed"
                        ? "bg-success"
                        : "bg-border"
                    }`} />
                  )}
                </div>

                {/* Round Info */}
                <button
                  onClick={() => setActiveTab(round.id.toString())}
                  className={`flex-1 text-left pb-6 rounded-lg px-2 py-1 -ml-1 transition-all ${
                    activeTab === round.id.toString()
                      ? "bg-primary/5"
                      : "hover:bg-muted/30"
                  }`}
                >
                  <span className={`text-sm font-semibold block ${
                    activeTab === round.id.toString() ? "text-primary" : "text-foreground"
                  }`}>{round.name}</span>
                  {round.date && (
                    <span className="text-xs text-muted-foreground">{round.date}</span>
                  )}
                  {round.status === "not-set" && (
                    <span className="text-xs text-muted-foreground">Not configured</span>
                  )}
                </button>
              </div>
            ))}
          </div>

          {/* Right: Content */}
          <div className="flex-1 min-w-0">
            {currentRound && (
              <Card className="border-border/50">
                <CardHeader className="border-b border-border/50 pb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="rounded-xl bg-muted p-2.5">
                        {statusIcon(currentRound.status, "h-5 w-5")}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-foreground">{currentRound.name}</h3>
                        <div className="flex items-center gap-2 mt-0.5">
                          {statusBadge(currentRound.status)}
                          {currentRound.date && (
                            <span className="text-xs text-muted-foreground">· {currentRound.date}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    {currentRound.candidates && (
                      <div className="text-right">
                        <p className="text-sm font-medium text-foreground">{currentRound.candidates.length}</p>
                        <p className="text-xs text-muted-foreground">Candidates</p>
                      </div>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="p-6">
                  {isNotSet ? (
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <Plus className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <h4 className="font-semibold text-foreground">Choose Next Round</h4>
                          <p className="text-sm text-muted-foreground">Select the type of round to add</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {nextRoundOptions.map((opt) => (
                          <button
                            key={opt.label}
                            className="flex items-center gap-3 rounded-xl border border-border/60 bg-card p-4 text-left hover:border-primary/50 hover:shadow-sm transition-all group"
                          >
                            <div className="rounded-lg bg-muted p-2.5 group-hover:bg-primary/10 transition-colors">
                              <opt.icon className="h-4.5 w-4.5 text-muted-foreground group-hover:text-primary transition-colors" />
                            </div>
                            <div>
                              <span className="text-sm font-semibold text-foreground">{opt.label}</span>
                              <p className="text-xs text-muted-foreground leading-snug">{opt.description}</p>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : currentRound.candidates ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-foreground flex items-center gap-2">
                          <User className="h-4 w-4 text-muted-foreground" />
                          Candidate Results
                        </h4>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-success font-medium">
                            {currentRound.candidates.filter(c => c.status === "passed").length} passed
                          </span>
                          <span className="text-muted-foreground">·</span>
                          <span className="text-destructive font-medium">
                            {currentRound.candidates.filter(c => c.status === "failed").length} failed
                          </span>
                          <span className="text-muted-foreground">·</span>
                          <span className="text-muted-foreground">
                            {currentRound.candidates.filter(c => c.status === "pending").length} pending
                          </span>
                        </div>
                      </div>
                      <div className="grid gap-2">
                        {currentRound.candidates
                          .sort((a, b) => b.score - a.score)
                          .map((candidate) => (
                            <div
                              key={candidate.name}
                              className={`flex items-center justify-between rounded-lg border px-4 py-3 ${candidateStatusStyle(candidate.status)}`}
                            >
                              <div className="flex items-center gap-3">
                                <div className="h-8 w-8 rounded-full bg-background flex items-center justify-center text-xs font-bold text-foreground">
                                  {candidate.name.split(" ").map(n => n[0]).join("")}
                                </div>
                                <span className="text-sm font-medium text-foreground">{candidate.name}</span>
                              </div>
                              <div className="flex items-center gap-4">
                                {candidate.score > 0 && (
                                  <span className="text-sm font-mono font-semibold">{candidate.score}/100</span>
                                )}
                                <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                                  candidate.status === "passed" ? "bg-success/20 text-success" :
                                  candidate.status === "failed" ? "bg-destructive/20 text-destructive" :
                                  "bg-muted text-muted-foreground"
                                }`}>
                                  {candidateStatusIcon(candidate.status)}
                                  <span className="capitalize">{candidate.status}</span>
                                </div>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="rounded-full bg-muted w-16 h-16 mx-auto flex items-center justify-center mb-4">
                        {statusIcon(currentRound.status, "h-8 w-8")}
                      </div>
                      <h4 className="font-semibold text-foreground mb-1">
                        {currentRound.status === "upcoming" ? "Round Not Started" : "No Candidates Yet"}
                      </h4>
                      <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                        {currentRound.status === "upcoming"
                          ? "This round is scheduled but hasn't started yet."
                          : "Candidate results will be displayed here once available."}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}