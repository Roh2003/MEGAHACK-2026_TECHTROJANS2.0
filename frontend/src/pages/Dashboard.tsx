import { DashboardLayout } from "@/components/DashboardLayout";
import { StatsCard } from "@/components/StatsCard";
import { ActiveJobCard } from "@/components/ActiveJobCard";
import { RecruitmentPipeline } from "@/components/RecruitmentPipeline";
import { RecentCandidates } from "@/components/RecentCandidates";
import { Briefcase, Users, CheckCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

const activeJobs = [
  {
    title: "Senior React Developer",
    department: "Engineering",
    location: "Bangalore, India",
    postedDate: "Mar 8, 2026",
    daysLeft: 2,
    totalApplicants: 124,
    shortlisted: 18,
    platforms: ["LinkedIn", "Naukri", "Indeed"],
    stage: "Resume Screening",
  },
  {
    title: "Product Designer",
    department: "Design",
    location: "Remote",
    postedDate: "Mar 6, 2026",
    daysLeft: 0,
    totalApplicants: 89,
    shortlisted: 12,
    platforms: ["LinkedIn", "Naukri"],
    stage: "Assessment Round",
  },
  {
    title: "DevOps Engineer",
    department: "Infrastructure",
    location: "Hyderabad, India",
    postedDate: "Mar 9, 2026",
    daysLeft: 3,
    totalApplicants: 56,
    shortlisted: 0,
    platforms: ["LinkedIn", "Indeed", "Naukri"],
    stage: "Accepting Applications",
  },
];

export default function Dashboard() {
  return (
    <DashboardLayout title="Dashboard">
      <div className="space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Active Job Posts"
            value={12}
            change="+3 this week"
            changeType="positive"
            icon={Briefcase}
          />
          <StatsCard
            title="Total Applicants"
            value={1248}
            change="+156 today"
            changeType="positive"
            icon={Users}
          />
          <StatsCard
            title="Hired This Month"
            value={8}
            change="67% of target"
            changeType="neutral"
            icon={CheckCircle}
          />
          <StatsCard
            title="Avg. Time to Hire"
            value="18d"
            change="-2d from last month"
            changeType="positive"
            icon={Clock}
          />
        </div>

        {/* Active Jobs */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-display font-bold text-foreground">Active Job Posts</h2>
            <Button size="sm" className="gap-1.5">
              <Plus className="h-4 w-4" /> New Job Post
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {activeJobs.map((job) => (
              <ActiveJobCard key={job.title} {...job} />
            ))}
          </div>
        </div>

        {/* Pipeline + Candidates */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RecruitmentPipeline />
          <RecentCandidates />
        </div>
      </div>
    </DashboardLayout>
  );
}
