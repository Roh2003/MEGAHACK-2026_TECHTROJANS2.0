import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Calendar, Users, ChevronRight } from "lucide-react";

const pastJobs = [
  { title: "Java Fullstack Developer", dept: "Engineering", closedDate: "Feb 28, 2026", hired: 3, totalApplicants: 210, matchingFromPast: 12 },
  { title: "UX Researcher", dept: "Design", closedDate: "Feb 15, 2026", hired: 1, totalApplicants: 95, matchingFromPast: 4 },
  { title: "ML Engineer", dept: "AI/ML", closedDate: "Jan 30, 2026", hired: 2, totalApplicants: 178, matchingFromPast: 8 },
  { title: "QA Automation Lead", dept: "Quality", closedDate: "Jan 10, 2026", hired: 1, totalApplicants: 142, matchingFromPast: 6 },
];

export default function History() {
  return (
    <DashboardLayout title="Hiring History">
      <div className="space-y-6">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search past job posts..." className="pl-9" />
        </div>

        <div className="space-y-3">
          {pastJobs.map((job) => (
            <Card key={job.title} className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-3">
                      <h3 className="font-display font-bold text-foreground">{job.title}</h3>
                      <Badge variant="secondary">{job.dept}</Badge>
                    </div>
                    <div className="flex items-center gap-5 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" /> Closed {job.closedDate}</span>
                      <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> {job.totalApplicants} applicants</span>
                      <span className="text-success font-medium">{job.hired} hired</span>
                    </div>
                    {job.matchingFromPast > 0 && (
                      <p className="text-xs text-info font-medium">
                        💡 {job.matchingFromPast} matching candidates from past rejections available
                      </p>
                    )}
                  </div>
                  <Button variant="ghost" size="sm" className="text-primary gap-1">
                    View <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
