import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Clock, Users, FileText } from "lucide-react";

const assessments = [
  { id: 1, title: "React Frontend Assessment", job: "Senior React Developer", type: "Technical", questions: 25, duration: "60 min", candidates: 18, status: "Active", startDate: "Mar 10", endDate: "Mar 12" },
  { id: 2, title: "Aptitude Test - Batch 2", job: "Frontend Intern", type: "Aptitude", questions: 40, duration: "45 min", candidates: 45, status: "Completed", startDate: "Mar 7", endDate: "Mar 9" },
  { id: 3, title: "System Design Round", job: "DevOps Engineer", type: "Technical", questions: 5, duration: "90 min", candidates: 12, status: "Scheduled", startDate: "Mar 13", endDate: "Mar 14" },
];

export default function Assessments() {
  return (
    <DashboardLayout title="Assessments">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <p className="text-muted-foreground">Create and manage assessment tests for candidates</p>
          <Button className="gap-1.5">
            <Plus className="h-4 w-4" /> Create Assessment
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {assessments.map((a) => (
            <Card key={a.id} className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="font-display text-base">{a.title}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">{a.job}</p>
                  </div>
                  <Badge
                    variant={a.status === "Active" ? "default" : "secondary"}
                    className={
                      a.status === "Active" ? "bg-success/10 text-success border-0" :
                      a.status === "Scheduled" ? "bg-info/10 text-info border-0" : ""
                    }
                  >
                    {a.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1"><FileText className="h-3.5 w-3.5" /> {a.questions} Q</span>
                  <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> {a.duration}</span>
                  <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> {a.candidates}</span>
                </div>
                <Badge variant="outline" className="text-xs">{a.type}</Badge>
                <p className="text-xs text-muted-foreground">
                  {a.startDate} → {a.endDate}
                </p>
                <Button variant="outline" size="sm" className="w-full mt-2">
                  View Details
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
