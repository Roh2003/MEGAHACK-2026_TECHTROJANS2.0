import { useState } from "react";
import { useAssessment } from "@/context/AssessmentContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ArrowLeft, ArrowRight } from "lucide-react";

const CandidateDetailsForm = () => {
  const { setStep, setCandidate, startTimer } = useAssessment();
  const [form, setForm] = useState({ fullName: "", email: "", phone: "", jobRole: "" });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.fullName.trim()) errs.fullName = "Full name is required";
    if (!form.email.trim() || !/\S+@\S+\.\S+/.test(form.email)) errs.email = "Valid email is required";
    if (!form.phone.trim() || form.phone.trim().length < 7) errs.phone = "Valid phone number is required";
    if (!form.jobRole.trim()) errs.jobRole = "Job role is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setCandidate(form);
    startTimer();
    setStep("assessment");
  };

  const fields = [
    { key: "fullName", label: "Full Name", type: "text", placeholder: "John Doe" },
    { key: "email", label: "Email Address", type: "email", placeholder: "john@example.com" },
    { key: "phone", label: "Phone Number", type: "tel", placeholder: "+1 234 567 890" },
    { key: "jobRole", label: "Job Role Applying For", type: "text", placeholder: "Software Engineer" },
  ] as const;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md shadow-lg border-0 bg-card">
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-2xl">Your Details</CardTitle>
          <CardDescription>Please fill in your information before starting the assessment.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map(({ key, label, type, placeholder }) => (
              <div key={key} className="space-y-1.5">
                <Label htmlFor={key} className="text-sm font-medium">{label}</Label>
                <Input
                  id={key}
                  type={type}
                  placeholder={placeholder}
                  value={form[key]}
                  onChange={e => setForm(prev => ({ ...prev, [key]: e.target.value }))}
                  className={errors[key] ? "border-destructive" : ""}
                />
                {errors[key] && <p className="text-xs text-destructive">{errors[key]}</p>}
              </div>
            ))}
            <div className="flex gap-3 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={() => setStep("landing")}>
                <ArrowLeft className="h-4 w-4 mr-1" /> Back
              </Button>
              <Button type="submit" className="flex-1">
                Begin Test <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CandidateDetailsForm;
