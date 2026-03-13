import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Upload, Plus } from "lucide-react";

const offers = [
  { candidate: "Kavita Singh", role: "Data Scientist", status: "Sent", date: "Mar 10, 2026", type: "Generated" },
  { candidate: "Arjun Sharma", role: "Senior React Developer", status: "Accepted", date: "Mar 8, 2026", type: "Uploaded" },
  { candidate: "Ravi Nair", role: "ML Engineer", status: "Pending", date: "Mar 11, 2026", type: "Generated" },
];

export default function Offers() {
  return (
    <DashboardLayout title="Offer Letters">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <p className="text-muted-foreground">Generate or upload offer letters for selected candidates</p>
          <div className="flex gap-2">
            <Button variant="outline" className="gap-1.5">
              <Upload className="h-4 w-4" /> Upload Letter
            </Button>
            <Button className="gap-1.5">
              <Plus className="h-4 w-4" /> Generate Offer
            </Button>
          </div>
        </div>

        <div className="space-y-3">
          {offers.map((o) => (
            <Card key={o.candidate} className="border-border/50 shadow-sm">
              <CardContent className="p-5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center">
                    <FileText className="h-5 w-5 text-accent-foreground" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{o.candidate}</p>
                    <p className="text-sm text-muted-foreground">{o.role} • {o.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className="text-xs">{o.type}</Badge>
                  <Badge className={`text-xs border-0 ${
                    o.status === "Accepted" ? "bg-success/10 text-success" :
                    o.status === "Sent" ? "bg-info/10 text-info" :
                    "bg-warning/10 text-warning"
                  }`}>
                    {o.status}
                  </Badge>
                  <Button variant="ghost" size="sm" className="text-primary text-xs">View</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
