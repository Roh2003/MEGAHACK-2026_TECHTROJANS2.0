import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { MapPin, Clock, Users, ExternalLink } from "lucide-react";

interface ActiveJobCardProps {
  title: string;
  department: string;
  location: string;
  postedDate: string;
  daysLeft: number;
  totalApplicants: number;
  shortlisted: number;
  platforms: string[];
  stage: string;
}

export function ActiveJobCard({
  title,
  department,
  location,
  postedDate,
  daysLeft,
  totalApplicants,
  shortlisted,
  platforms,
  stage,
}: ActiveJobCardProps) {
  const progressValue = daysLeft <= 0 ? 100 : Math.max(0, 100 - (daysLeft / 3) * 100);

  return (
    <Card className="border-border/50 shadow-sm hover:shadow-md transition-all">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-display font-bold text-foreground text-lg">{title}</h3>
            <p className="text-sm text-muted-foreground">{department}</p>
          </div>
          <Badge
            variant={daysLeft <= 0 ? "destructive" : daysLeft <= 1 ? "secondary" : "default"}
            className={daysLeft > 1 ? "bg-primary/10 text-primary border-0" : ""}
          >
            {daysLeft <= 0 ? "Closed" : `${daysLeft}d left`}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <MapPin className="h-3.5 w-3.5" /> {location}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" /> {postedDate}
          </span>
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Application timeline</span>
            <span className="font-medium text-foreground">{Math.round(progressValue)}%</span>
          </div>
          <Progress value={progressValue} className="h-1.5" />
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-sm">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium text-foreground">{totalApplicants}</span>
            <span className="text-muted-foreground">applicants</span>
          </div>
          <div className="text-sm">
            <span className="font-medium text-success">{shortlisted}</span>
            <span className="text-muted-foreground"> shortlisted</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Posted on:</span>
          <div className="flex gap-1.5">
            {platforms.map((p) => (
              <Badge key={p} variant="outline" className="text-xs font-normal py-0 h-5">
                {p}
              </Badge>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-border/50">
          <Badge variant="secondary" className="text-xs">
            {stage}
          </Badge>
          <Button variant="ghost" size="sm" className="text-primary text-xs gap-1">
            View Details <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
