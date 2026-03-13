import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { toast } from "@/hooks/use-toast";
import {
  CalendarIcon,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  Briefcase,
  MapPin,
  FileText,
  Wrench,
  IndianRupee,
  X,
  Sparkles,
} from "lucide-react";

const SKILL_OPTIONS = [
  "Python", "JavaScript", "TypeScript", "React", "Angular", "Vue.js",
  "Node.js", "FastAPI", "Django", "Flask", "Java", "Spring Boot",
  "Go", "Rust", "C++", "MongoDB", "PostgreSQL", "MySQL", "Redis",
  "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD",
  "GraphQL", "REST API", "Microservices", "System Design", "Data Structures",
  "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
  "Figma", "Adobe XD", "Sketch", "UI/UX Design", "Agile", "Scrum",
];

const EXPERIENCE_OPTIONS = [
  "0-1 years", "1-3 years", "3-5 years", "5-8 years", "8-12 years", "12+ years",
];

const steps = [
  { id: 1, title: "Basic Info", icon: Briefcase, description: "Title, location & description" },
  { id: 2, title: "Skills & Experience", icon: Wrench, description: "Required skillset" },
  { id: 3, title: "Compensation & Timeline", icon: IndianRupee, description: "CTC, dates & review" },
];

export default function CreateJob() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [skillSearch, setSkillSearch] = useState("");

  const [formData, setFormData] = useState({
    title: "",
    location: "",
    description: "",
    skills: [] as string[],
    experience: "",
    ctc: "",
    startDate: undefined as Date | undefined,
    endDate: undefined as Date | undefined,
  });

  const updateField = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const addSkill = (skill: string) => {
    if (!formData.skills.includes(skill)) {
      updateField("skills", [...formData.skills, skill]);
    }
    setSkillSearch("");
  };

  const removeSkill = (skill: string) => {
    updateField("skills", formData.skills.filter((s) => s !== skill));
  };

  const filteredSkills = SKILL_OPTIONS.filter(
    (s) =>
      s.toLowerCase().includes(skillSearch.toLowerCase()) &&
      !formData.skills.includes(s)
  );

  const canProceed = () => {
    if (currentStep === 1) return formData.title.trim() && formData.location.trim();
    if (currentStep === 2) return formData.skills.length > 0 && formData.experience;
    return true;
  };

  const handleSubmit = () => {
    const payload = {
      title: formData.title,
      skills: formData.skills,
      description: formData.description || null,
      experience: formData.experience,
      location: formData.location,
      ctc: formData.ctc,
      start_time: formData.startDate?.toISOString() || null,
      end_time: formData.endDate?.toISOString() || null,
    };
    console.log("Job Post Payload:", payload);
    toast({
      title: "Job Post Created!",
      description: `"${formData.title}" has been created successfully.`,
    });
    navigate("/jobs");
  };

  return (
    <DashboardLayout title="Create Job Post">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Step Indicator */}
        <div className="flex items-center justify-between">
          {steps.map((step, idx) => (
            <div key={step.id} className="flex items-center flex-1">
              <button
                onClick={() => step.id < currentStep && setCurrentStep(step.id)}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-xl transition-all w-full",
                  currentStep === step.id
                    ? "bg-primary/10 border-2 border-primary"
                    : step.id < currentStep
                    ? "bg-success/10 border-2 border-success cursor-pointer"
                    : "bg-muted border-2 border-transparent"
                )}
              >
                <div
                  className={cn(
                    "h-10 w-10 rounded-full flex items-center justify-center shrink-0",
                    currentStep === step.id
                      ? "bg-primary text-primary-foreground"
                      : step.id < currentStep
                      ? "bg-success text-success-foreground"
                      : "bg-muted-foreground/20 text-muted-foreground"
                  )}
                >
                  {step.id < currentStep ? (
                    <CheckCircle2 className="h-5 w-5" />
                  ) : (
                    <step.icon className="h-5 w-5" />
                  )}
                </div>
                <div className="text-left">
                  <p
                    className={cn(
                      "text-sm font-semibold",
                      currentStep === step.id
                        ? "text-primary"
                        : step.id < currentStep
                        ? "text-success"
                        : "text-muted-foreground"
                    )}
                  >
                    {step.title}
                  </p>
                  <p className="text-xs text-muted-foreground">{step.description}</p>
                </div>
              </button>
              {idx < steps.length - 1 && (
                <ChevronRight
                  className={cn(
                    "h-5 w-5 mx-2 shrink-0",
                    step.id < currentStep ? "text-success" : "text-muted-foreground/40"
                  )}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <Card className="border-border/50 shadow-lg">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-xl">
              <Sparkles className="h-5 w-5 text-primary" />
              {steps[currentStep - 1].title}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Step 1: Basic Info */}
            {currentStep === 1 && (
              <div className="space-y-5">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">
                    Job Title <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="e.g. Senior Python Developer"
                      value={formData.title}
                      onChange={(e) => updateField("title", e.target.value)}
                      className="pl-10 h-12"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">
                    Location <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="e.g. Pune, India"
                      value={formData.location}
                      onChange={(e) => updateField("location", e.target.value)}
                      className="pl-10 h-12"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    Job Description
                  </label>
                  <Textarea
                    placeholder="Describe the role, responsibilities, and what you're looking for..."
                    value={formData.description}
                    onChange={(e) => updateField("description", e.target.value)}
                    className="min-h-[140px] resize-none"
                  />
                </div>
              </div>
            )}

            {/* Step 2: Skills & Experience */}
            {currentStep === 2 && (
              <div className="space-y-5">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">
                    Required Skills <span className="text-destructive">*</span>
                  </label>

                  {/* Selected Skills */}
                  {formData.skills.length > 0 && (
                    <div className="flex flex-wrap gap-2 p-3 rounded-lg bg-accent/30 border border-accent">
                      {formData.skills.map((skill) => (
                        <Badge
                          key={skill}
                          className="bg-primary/15 text-primary border-primary/30 hover:bg-primary/25 gap-1 px-3 py-1.5 cursor-pointer transition-colors"
                          onClick={() => removeSkill(skill)}
                        >
                          {skill}
                          <X className="h-3 w-3" />
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Skill Search */}
                  <Input
                    placeholder="Search skills to add..."
                    value={skillSearch}
                    onChange={(e) => setSkillSearch(e.target.value)}
                    className="h-12"
                  />

                  {/* Skill Suggestions */}
                  <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
                    {(skillSearch ? filteredSkills : SKILL_OPTIONS.filter((s) => !formData.skills.includes(s)).slice(0, 12)).map(
                      (skill) => (
                        <Badge
                          key={skill}
                          variant="outline"
                          className="cursor-pointer hover:bg-primary/10 hover:border-primary/40 transition-colors px-3 py-1.5"
                          onClick={() => addSkill(skill)}
                        >
                          + {skill}
                        </Badge>
                      )
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">
                    Experience Required <span className="text-destructive">*</span>
                  </label>
                  <Select
                    value={formData.experience}
                    onValueChange={(v) => updateField("experience", v)}
                  >
                    <SelectTrigger className="h-12">
                      <SelectValue placeholder="Select experience range" />
                    </SelectTrigger>
                    <SelectContent>
                      {EXPERIENCE_OPTIONS.map((exp) => (
                        <SelectItem key={exp} value={exp}>
                          {exp}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {/* Step 3: Compensation & Timeline */}
            {currentStep === 3 && (
              <div className="space-y-5">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">CTC Range</label>
                  <div className="relative">
                    <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="e.g. 12-18 LPA"
                      value={formData.ctc}
                      onChange={(e) => updateField("ctc", e.target.value)}
                      className="pl-10 h-12"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-foreground">Start Date</label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full h-12 justify-start text-left font-normal",
                            !formData.startDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {formData.startDate ? format(formData.startDate, "PPP") : "Pick start date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={formData.startDate}
                          onSelect={(d) => updateField("startDate", d)}
                          initialFocus
                          className="p-3 pointer-events-auto"
                        />
                      </PopoverContent>
                    </Popover>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-foreground">End Date</label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full h-12 justify-start text-left font-normal",
                            !formData.endDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {formData.endDate ? format(formData.endDate, "PPP") : "Pick end date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={formData.endDate}
                          onSelect={(d) => updateField("endDate", d)}
                          initialFocus
                          className="p-3 pointer-events-auto"
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>

                {/* Review Summary */}
                <div className="mt-4 p-5 rounded-xl bg-accent/20 border border-accent space-y-3">
                  <h4 className="font-semibold text-foreground flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-primary" /> Review Summary
                  </h4>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-muted-foreground">Title:</span>{" "}
                      <span className="font-medium text-foreground">{formData.title || "—"}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Location:</span>{" "}
                      <span className="font-medium text-foreground">{formData.location || "—"}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Experience:</span>{" "}
                      <span className="font-medium text-foreground">{formData.experience || "—"}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">CTC:</span>{" "}
                      <span className="font-medium text-foreground">{formData.ctc || "—"}</span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-muted-foreground">Skills:</span>{" "}
                      <span className="font-medium text-foreground">
                        {formData.skills.length > 0 ? formData.skills.join(", ") : "—"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => (currentStep === 1 ? navigate("/jobs") : setCurrentStep(currentStep - 1))}
            className="gap-1.5"
          >
            <ChevronLeft className="h-4 w-4" />
            {currentStep === 1 ? "Cancel" : "Back"}
          </Button>

          {currentStep < 3 ? (
            <Button
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!canProceed()}
              className="gap-1.5"
            >
              Next <ChevronRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} className="gap-1.5 px-8">
              <Sparkles className="h-4 w-4" /> Create Job Post
            </Button>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
