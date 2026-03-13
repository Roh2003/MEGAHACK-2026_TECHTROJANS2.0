import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Plus, Search, MapPin, Users, Calendar, MoreVertical, Activity, Pencil, Trash2 } from "lucide-react";

const jobs = [
  { id: 1, title: "Senior React Developer", dept: "Engineering", location: "Bangalore", type: "Full-time", applicants: 124, status: "Active", deadline: "Mar 11, 2026", platforms: ["LinkedIn", "Naukri", "Indeed"] },
  { id: 2, title: "Product Designer", dept: "Design", location: "Remote", type: "Full-time", applicants: 89, status: "Closed", deadline: "Mar 6, 2026", platforms: ["LinkedIn", "Naukri"] },
  { id: 3, title: "DevOps Engineer", dept: "Infrastructure", location: "Hyderabad", type: "Full-time", applicants: 56, status: "Active", deadline: "Mar 12, 2026", platforms: ["LinkedIn", "Indeed", "Naukri"] },
  { id: 4, title: "Data Scientist", dept: "Analytics", location: "Mumbai", type: "Full-time", applicants: 203, status: "Active", deadline: "Mar 14, 2026", platforms: ["LinkedIn"] },
  { id: 5, title: "Frontend Intern", dept: "Engineering", location: "Remote", type: "Internship", applicants: 312, status: "Active", deadline: "Mar 13, 2026", platforms: ["Naukri", "Indeed"] },
];

export default function Jobs() {
  const navigate = useNavigate();

  return (
    <DashboardLayout title="Job Posts">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search job posts..." className="pl-9" />
          </div>
          <Button className="gap-1.5 shrink-0" onClick={() => navigate("/jobs/create")}>
            <Plus className="h-4 w-4" /> Create Job Post
          </Button>
        </div>

        <div className="space-y-3">
          {jobs.map((job) => (
            <Card key={job.id} className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-display font-bold text-foreground text-lg">{job.title}</h3>
                      <Badge variant={job.status === "Active" ? "default" : "secondary"}
                        className={job.status === "Active" ? "bg-success/10 text-success border-0" : ""}>
                        {job.status}
                      </Badge>
                      <Badge variant="outline" className="text-xs">{job.type}</Badge>
                    </div>
                    <div className="flex items-center gap-5 text-sm text-muted-foreground">
                      <span>{job.dept}</span>
                      <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {job.location}</span>
                      <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> {job.applicants} applicants</span>
                      <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" /> {job.deadline}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Platforms:</span>
                      {job.platforms.map((p) => (
                        <Badge key={p} variant="outline" className="text-xs font-normal py-0 h-5">{p}</Badge>
                      ))}
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="shrink-0">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => navigate(`/jobs/${job.id}/progress`)}>
                        <Activity className="h-4 w-4 mr-2" />
                        Progress
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Pencil className="h-4 w-4 mr-2" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
