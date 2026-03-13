import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Search, Download, Filter } from "lucide-react";

const candidates = [
  { name: "Arjun Sharma", email: "arjun@email.com", role: "Senior React Developer", score: 92, stage: "AI Interview", skills: ["React", "TypeScript", "Node.js"], initials: "AS" },
  { name: "Priya Patel", email: "priya@email.com", role: "Full Stack Engineer", score: 88, stage: "Assessment", skills: ["Python", "Django", "React"], initials: "PP" },
  { name: "Rahul Kumar", email: "rahul@email.com", role: "Backend Developer", score: 85, stage: "Shortlisted", skills: ["Java", "Spring Boot", "AWS"], initials: "RK" },
  { name: "Sneha Gupta", email: "sneha@email.com", role: "DevOps Engineer", score: 79, stage: "Resume Review", skills: ["Docker", "K8s", "Terraform"], initials: "SG" },
  { name: "Amit Verma", email: "amit@email.com", role: "Senior React Developer", score: 76, stage: "Applied", skills: ["React", "Redux", "CSS"], initials: "AV" },
  { name: "Kavita Singh", email: "kavita@email.com", role: "Data Scientist", score: 94, stage: "Final Interview", skills: ["Python", "ML", "TensorFlow"], initials: "KS" },
  { name: "Vikram Joshi", email: "vikram@email.com", role: "Frontend Intern", score: 71, stage: "Rejected", skills: ["HTML", "CSS", "JavaScript"], initials: "VJ" },
];

const stageColors: Record<string, string> = {
  "AI Interview": "bg-primary/10 text-primary",
  "Assessment": "bg-warning/10 text-warning",
  "Shortlisted": "bg-success/10 text-success",
  "Resume Review": "bg-info/10 text-info",
  "Applied": "bg-muted text-muted-foreground",
  "Final Interview": "bg-primary/15 text-primary",
  "Rejected": "bg-destructive/10 text-destructive",
};

export default function Candidates() {
  return (
    <DashboardLayout title="Candidates">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search candidates..." className="pl-9" />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-1.5">
              <Filter className="h-4 w-4" /> Filter
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5">
              <Download className="h-4 w-4" /> Export
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          {candidates.map((c) => (
            <Card key={c.email} className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">
                        {c.initials}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium text-foreground">{c.name}</p>
                      <p className="text-sm text-muted-foreground">{c.role} • {c.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="hidden md:flex gap-1.5">
                      {c.skills.map((s) => (
                        <Badge key={s} variant="outline" className="text-xs font-normal">{s}</Badge>
                      ))}
                    </div>
                    <div className="text-center min-w-[50px]">
                      <p className="text-xl font-display font-bold text-foreground">{c.score}</p>
                      <p className="text-[10px] text-muted-foreground">Score</p>
                    </div>
                    <Badge className={`text-xs border-0 min-w-[90px] justify-center ${stageColors[c.stage] || ""}`}>
                      {c.stage}
                    </Badge>
                    <Button variant="ghost" size="sm" className="text-primary text-xs">
                      View
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
