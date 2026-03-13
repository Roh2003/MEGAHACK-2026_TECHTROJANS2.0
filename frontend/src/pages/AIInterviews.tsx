import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Bot, Video, MapPin, Plus } from "lucide-react";

const interviews = [
  { id: 1, candidate: "Arjun Sharma", initials: "AS", role: "Senior React Developer", type: "AI Interview", score: 87, confidence: 82, english: 91, status: "Completed", date: "Mar 10" },
  { id: 2, candidate: "Priya Patel", initials: "PP", role: "Full Stack Engineer", type: "Video Call", score: null, confidence: null, english: null, status: "Scheduled", date: "Mar 12" },
  { id: 3, candidate: "Kavita Singh", initials: "KS", role: "Data Scientist", type: "In-Person", score: null, confidence: null, english: null, status: "Scheduled", date: "Mar 13" },
];

const typeIcons = {
  "AI Interview": Bot,
  "Video Call": Video,
  "In-Person": MapPin,
};

export default function AIInterviews() {
  return (
    <DashboardLayout title="Interviews">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <p className="text-muted-foreground">Manage AI interviews, video calls, and in-person meetings</p>
          <Button className="gap-1.5">
            <Plus className="h-4 w-4" /> Schedule Interview
          </Button>
        </div>

        {/* Interview type cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { type: "AI Interview", desc: "AI-powered voice interviews with automated scoring", icon: Bot, count: 8 },
            { type: "Video Call", desc: "Online face-to-face technical interviews", icon: Video, count: 12 },
            { type: "In-Person", desc: "On-site office interviews", icon: MapPin, count: 5 },
          ].map((t) => (
            <Card key={t.type} className="border-border/50 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-5 flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-accent flex items-center justify-center shrink-0">
                  <t.icon className="h-6 w-6 text-accent-foreground" />
                </div>
                <div>
                  <p className="font-display font-bold text-foreground">{t.type}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{t.desc}</p>
                  <p className="text-sm font-medium text-primary mt-1">{t.count} scheduled</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent interviews */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle className="font-display text-lg">Recent Interviews</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {interviews.map((i) => {
              const Icon = typeIcons[i.type as keyof typeof typeIcons] || Bot;
              return (
                <div
                  key={i.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-muted/40 hover:bg-muted/70 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">
                        {i.initials}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium text-foreground">{i.candidate}</p>
                      <p className="text-sm text-muted-foreground">{i.role}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                      <Icon className="h-4 w-4" /> {i.type}
                    </div>
                    {i.score !== null ? (
                      <div className="text-center">
                        <p className="text-xl font-display font-bold text-foreground">{i.score}</p>
                        <p className="text-[10px] text-muted-foreground">Score</p>
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">{i.date}</p>
                    )}
                    <Badge
                      className={`text-xs border-0 ${
                        i.status === "Completed"
                          ? "bg-success/10 text-success"
                          : "bg-info/10 text-info"
                      }`}
                    >
                      {i.status}
                    </Badge>
                    <Button variant="ghost" size="sm" className="text-primary text-xs">
                      {i.status === "Completed" ? "View Report" : "Details"}
                    </Button>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
