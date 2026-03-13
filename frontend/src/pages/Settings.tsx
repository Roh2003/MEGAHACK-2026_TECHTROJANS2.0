import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export default function Settings() {
  return (
    <DashboardLayout title="Settings">
      <div className="max-w-2xl space-y-6">
        <Card className="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle className="font-display">Platform Integrations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {["LinkedIn", "Naukri.com", "Indeed", "Glassdoor"].map((p) => (
              <div key={p} className="flex items-center justify-between p-3 rounded-lg bg-muted/40">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-foreground">{p}</span>
                  <Badge variant="outline" className="text-xs">API</Badge>
                </div>
                <Switch defaultChecked={p !== "Glassdoor"} />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle className="font-display">Email Notifications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              "Send rejection emails with reasons",
              "Notify candidates on shortlisting",
              "Send assessment links automatically",
              "Send offer letter via email",
            ].map((setting) => (
              <div key={setting} className="flex items-center justify-between">
                <Label className="text-sm text-foreground">{setting}</Label>
                <Switch defaultChecked />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
