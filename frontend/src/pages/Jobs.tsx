import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/lib/axios";
import axios from "axios";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Plus, Search, MapPin, Users, Calendar, MoreVertical, Activity, Pencil, Trash2 } from "lucide-react";

interface JobPost {
  id: string;
  title: string;
  description: string | null;
  skills: string[];
  experience: string;
  location: string;
  ctc: string;
  start_time: string | null;
  end_time: string | null;
  created_by: string;
  created_at: string;
}

export default function Jobs() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<JobPost[]>([]);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchJobs = async () => {
      const accessToken = localStorage.getItem("access_token");
      if (!accessToken) {
        setError("Please login to view job posts.");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError("");
        const response = await apiClient.get<JobPost[]>("/job-posts", {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        setJobs(response.data || []);
      } catch (err) {
        const message = axios.isAxiosError(err)
          ? (err.response?.data?.message ?? err.response?.data?.detail ?? "Failed to fetch jobs.")
          : "Something went wrong. Please try again.";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    };

    void fetchJobs();
  }, []);

  const filteredJobs = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return jobs;
    return jobs.filter((job) => {
      return (
        job.title.toLowerCase().includes(q) ||
        job.location.toLowerCase().includes(q) ||
        job.experience.toLowerCase().includes(q) ||
        job.skills.some((s) => s.toLowerCase().includes(q))
      );
    });
  }, [jobs, query]);

  const getStatus = (job: JobPost) => {
    if (!job.end_time) return "Active";
    const end = new Date(job.end_time);
    return end.getTime() >= Date.now() ? "Active" : "Closed";
  };

  const formatDate = (iso: string | null) => {
    if (!iso) return "-";
    return new Date(iso).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <DashboardLayout title="Job Posts">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search job posts..."
              className="pl-9"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <Button className="gap-1.5 shrink-0" onClick={() => navigate("/jobs/create")}>
            <Plus className="h-4 w-4" /> Create Job Post
          </Button>
        </div>

        {isLoading ? (
          <Card className="border-border/50 shadow-sm">
            <CardContent className="p-6 text-sm text-muted-foreground">Loading job posts...</CardContent>
          </Card>
        ) : error ? (
          <Card className="border-destructive/30 shadow-sm">
            <CardContent className="p-6 flex items-center justify-between gap-3">
              <p className="text-sm text-destructive">{error}</p>
              <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
                Retry
              </Button>
            </CardContent>
          </Card>
        ) : filteredJobs.length === 0 ? (
          <Card className="border-border/50 shadow-sm">
            <CardContent className="p-6 text-sm text-muted-foreground">
              No jobs found. Create a new job post to get started.
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {filteredJobs.map((job) => (
            <Card key={job.id} className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-display font-bold text-foreground text-lg">{job.title}</h3>
                      <Badge
                        variant={getStatus(job) === "Active" ? "default" : "secondary"}
                        className={getStatus(job) === "Active" ? "bg-success/10 text-success border-0" : ""}
                      >
                        {getStatus(job)}
                      </Badge>
                      <Badge variant="outline" className="text-xs">{job.experience}</Badge>
                    </div>
                    <div className="flex items-center gap-5 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {job.location}</span>
                      <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> {job.skills.length} skills</span>
                      <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" /> {formatDate(job.end_time)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Skills:</span>
                      {job.skills.slice(0, 5).map((skill) => (
                        <Badge key={skill} variant="outline" className="text-xs font-normal py-0 h-5">{skill}</Badge>
                      ))}
                      {job.skills.length > 5 && (
                        <Badge variant="outline" className="text-xs font-normal py-0 h-5">+{job.skills.length - 5}</Badge>
                      )}
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
        )}
      </div>
    </DashboardLayout>
  );
}
