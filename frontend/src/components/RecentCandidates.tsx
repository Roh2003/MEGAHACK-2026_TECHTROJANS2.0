import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const candidates = [
  { name: "Arjun Sharma", role: "Senior React Dev", score: 92, stage: "Interview", initials: "AS" },
  { name: "Priya Patel", role: "Full Stack Engineer", score: 88, stage: "Assessment", initials: "PP" },
  { name: "Rahul Kumar", role: "Backend Developer", score: 85, stage: "Shortlisted", initials: "RK" },
  { name: "Sneha Gupta", role: "DevOps Engineer", score: 79, stage: "Resume Review", initials: "SG" },
  { name: "Amit Verma", role: "Senior React Dev", score: 76, stage: "Applied", initials: "AV" },
];

const stageColors: Record<string, string> = {
  Interview: "bg-primary/10 text-primary",
  Assessment: "bg-warning/10 text-warning",
  Shortlisted: "bg-success/10 text-success",
  "Resume Review": "bg-info/10 text-info",
  Applied: "bg-muted text-muted-foreground",
};

export function RecentCandidates() {
  return (
    <Card className="border-border/50 shadow-sm">
      <CardHeader>
        <CardTitle className="font-display text-lg">Top Candidates</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {candidates.map((c) => (
            <div
              key={c.name}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/40 hover:bg-muted/70 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Avatar className="h-9 w-9">
                  <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                    {c.initials}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium text-foreground">{c.name}</p>
                  <p className="text-xs text-muted-foreground">{c.role}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-lg font-display font-bold text-foreground">{c.score}</p>
                  <p className="text-[10px] text-muted-foreground">Match Score</p>
                </div>
                <Badge className={`text-[10px] border-0 ${stageColors[c.stage] || ""}`}>
                  {c.stage}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
