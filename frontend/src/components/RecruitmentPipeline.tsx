import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const stages = [
  { name: "Applied", count: 245, color: "bg-info" },
  { name: "Resume Screening", count: 180, color: "bg-primary" },
  { name: "Shortlisted", count: 45, color: "bg-warning" },
  { name: "Assessment", count: 30, color: "bg-accent-foreground" },
  { name: "Interview", count: 18, color: "bg-primary" },
  { name: "Offer", count: 5, color: "bg-success" },
];

export function RecruitmentPipeline() {
  const maxCount = Math.max(...stages.map((s) => s.count));

  return (
    <Card className="border-border/50 shadow-sm">
      <CardHeader>
        <CardTitle className="font-display text-lg">Recruitment Pipeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {stages.map((stage) => (
            <div key={stage.name} className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground w-36 shrink-0 text-right">
                {stage.name}
              </span>
              <div className="flex-1 h-8 bg-muted rounded-md overflow-hidden">
                <div
                  className={`h-full ${stage.color} rounded-md flex items-center px-3 transition-all`}
                  style={{ width: `${(stage.count / maxCount) * 100}%` }}
                >
                  <span className="text-xs font-semibold text-white">{stage.count}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
