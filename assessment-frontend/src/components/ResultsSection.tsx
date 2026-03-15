import { useAssessment } from "@/context/AssessmentContext";
import { Card, CardContent } from "@/components/ui/card";
import { Trophy, Target } from "lucide-react";

const ResultsSection = () => {
  const { candidate } = useAssessment();

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full space-y-8 text-center">
        <Card className="border-0 shadow-xl overflow-hidden">
          <div className="bg-primary px-6 py-8 text-primary-foreground space-y-3">
            <Trophy className="h-12 w-12 mx-auto opacity-90" />
            <h1 className="text-2xl font-bold">Assessment Complete!</h1>
            <p className="text-sm opacity-80">Thank you, {candidate?.fullName}</p>
          </div>
          <CardContent className="p-8 space-y-6">
            <div className="flex items-center gap-2 justify-center text-sm">
              <Target className="h-4 w-4 text-accent" />
              <span className="text-muted-foreground">Role: <span className="font-medium text-foreground">{candidate?.jobRole}</span></span>
            </div>

            <div className="rounded-xl bg-muted p-4 text-sm text-muted-foreground">
              Thank you for completing the assessment. Your results will be reviewed by the recruitment team. We'll be in touch soon.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ResultsSection;
