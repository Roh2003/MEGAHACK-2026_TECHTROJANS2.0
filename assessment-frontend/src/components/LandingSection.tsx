import { useAssessment } from "@/context/AssessmentContext";
import { Button } from "@/components/ui/button";
import { BrainCircuit, ClipboardCheck, Timer, ShieldCheck } from "lucide-react";

const features = [
  { icon: BrainCircuit, title: "AI-Powered", desc: "Smart assessment tailored to the role" },
  { icon: ClipboardCheck, title: "MCQ Format", desc: "Clear multiple-choice questions" },
  { icon: Timer, title: "Timed Test", desc: "15-minute countdown timer" },
  { icon: ShieldCheck, title: "Secure", desc: "Fair and monitored environment" },
];

const LandingSection = () => {
  const { setStep } = useAssessment();

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full text-center space-y-10">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary mb-4">
            <BrainCircuit className="h-4 w-4" />
            AI-Powered Recruitment
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-foreground">
            AI Candidate Assessment Portal
          </h1>
          <p className="text-lg text-muted-foreground mt-4 max-w-lg mx-auto">
            Complete your assessment as part of the recruitment process. Demonstrate your skills and knowledge in a fair, timed environment.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="rounded-xl border bg-card p-4 text-left space-y-2">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Icon className="h-5 w-5 text-primary" />
              </div>
              <p className="font-semibold text-sm text-card-foreground">{title}</p>
              <p className="text-xs text-muted-foreground">{desc}</p>
            </div>
          ))}
        </div>

        <Button
          size="lg"
          className="px-10 text-base h-12 rounded-xl font-semibold"
          onClick={() => setStep("details")}
        >
          Start Assessment
        </Button>
      </div>
    </div>
  );
};

export default LandingSection;
