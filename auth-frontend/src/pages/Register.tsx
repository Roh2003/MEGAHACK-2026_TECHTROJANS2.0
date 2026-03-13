import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import AuthSidePanel from "@/components/AuthSidePanel";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Check, Building2, User, Briefcase } from "lucide-react";
import { z } from "zod";
import { toast } from "sonner";
import axios from "axios";
import { apiClient } from "@/lib/axios";

const step1Schema = z.object({
  name: z.string().trim().min(1, "Name is required").max(100, "Name too long"),
  email: z.string().trim().email("Invalid email").max(255, "Email too long"),
  password: z.string().min(8, "Password must be at least 8 characters").max(128),
  phone_no: z.string().trim().min(10, "Phone number must be at least 10 digits").max(15).regex(/^\d+$/, "Phone must contain only digits"),
});

const step3Schema = z.object({
  org_name: z.string().trim().min(1, "Organization name is required").max(200),
  industry: z.string().trim().min(1, "Industry is required").max(100),
  size: z.number().min(1, "Size must be at least 1").max(1000000),
  location: z.string().trim().min(1, "Location is required").max(200),
});

const stepVariants = {
  enter: { opacity: 0, x: 30 },
  center: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -30 },
};

const Register = () => {
  const [step, setStep] = useState(1);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phoneNo, setPhoneNo] = useState("");

  const [role, setRole] = useState<"hr" | "candidate">("hr");

  const [orgName, setOrgName] = useState("");
  const [industry, setIndustry] = useState("");
  const [size, setSize] = useState("");
  const [location, setLocation] = useState("");

  const validateStep1 = () => {
    const result = step1Schema.safeParse({ name, email, password, phone_no: phoneNo });
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach((e) => { fieldErrors[e.path[0] as string] = e.message; });
      setErrors(fieldErrors);
      return false;
    }
    setErrors({});
    return true;
  };

  const validateStep3 = () => {
    const result = step3Schema.safeParse({ org_name: orgName, industry, size: Number(size), location });
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach((e) => { fieldErrors[e.path[0] as string] = e.message; });
      setErrors(fieldErrors);
      return false;
    }
    setErrors({});
    return true;
  };

  const nextStep = () => {
    if (step === 1 && !validateStep1()) return;
    if (step === 2 && role === "candidate") {
      handleSubmitCandidate();
      return;
    }
    setStep((s) => Math.min(s + 1, role === "hr" ? 3 : 2));
  };

  const prevStep = () => {
    setErrors({});
    setStep((s) => Math.max(s - 1, 1));
  };

  const handleSubmitCandidate = async () => {
    const payload = { name: name.trim(), email: email.trim(), password, role, phone_no: phoneNo.trim() };
    try {
      setIsSubmitting(true);
      await apiClient.post("/auth/register", payload);
      toast.success("Account created successfully!");
    } catch (error) {
      const message = axios.isAxiosError(error)
        ? (error.response?.data?.message ?? "Registration failed. Please try again.")
        : "Something went wrong. Please try again.";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitRecruiter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateStep3()) return;
    const payload = {
      name: name.trim(),
      email: email.trim(),
      password,
      role,
      phone_no: phoneNo.trim(),
      organization: {
        name: orgName.trim(),
        industry: industry.trim(),
        size: Number(size),
        location: location.trim(),
      },
    };
    try {
      setIsSubmitting(true);
      await apiClient.post("/auth/register", payload);
      toast.success("Organization account created successfully!");
    } catch (error) {
      const message = axios.isAxiosError(error)
        ? (error.response?.data?.message ?? "Registration failed. Please try again.")
        : "Something went wrong. Please try again.";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalSteps = role === "hr" ? 3 : 2;

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <AuthSidePanel />
      <div className="flex items-center justify-center p-6 sm:p-8 bg-background">
        <div className="w-full max-w-md">
          <Link to="/" className="flex items-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-lg bg-hero-gradient flex items-center justify-center">
              <span className="font-display font-bold text-primary-foreground text-sm">H</span>
            </div>
            <span className="font-display font-bold text-xl text-foreground">HireMind</span>
          </Link>

          <h1 className="font-display text-2xl font-bold text-foreground mb-1">Create your account</h1>
          <p className="text-muted-foreground text-sm mb-6">Get started with HireMind in seconds.</p>

          {/* Step indicator */}
          <div className="flex items-center gap-2 mb-8">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div key={i} className="flex items-center gap-2 flex-1">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold shrink-0 transition-colors ${
                  i + 1 < step ? "bg-primary text-primary-foreground"
                    : i + 1 === step ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
                }`}>
                  {i + 1 < step ? <Check size={14} /> : i + 1}
                </div>
                {i < totalSteps - 1 && <div className={`h-0.5 flex-1 rounded transition-colors ${i + 1 < step ? "bg-primary" : "bg-muted"}`} />}
              </div>
            ))}
          </div>

          <form onSubmit={step === totalSteps && role === "hr" ? handleSubmitRecruiter : (e) => { e.preventDefault(); nextStep(); }}>
            <AnimatePresence mode="wait">
              {step === 1 && (
                <motion.div key="step1" variants={stepVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.25 }} className="space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <User size={18} className="text-primary" />
                    <span className="font-display font-semibold text-foreground">Personal Details</span>
                  </div>
                  <div>
                    <Label htmlFor="name">Full Name</Label>
                    <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Rohit Sharma" className="mt-1.5 h-11" />
                    {errors.name && <p className="text-destructive text-xs mt-1">{errors.name}</p>}
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="rohit@techcorp.com" className="mt-1.5 h-11" />
                    {errors.email && <p className="text-destructive text-xs mt-1">{errors.email}</p>}
                  </div>
                  <div>
                    <Label htmlFor="password">Password</Label>
                    <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" className="mt-1.5 h-11" />
                    {errors.password && <p className="text-destructive text-xs mt-1">{errors.password}</p>}
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input id="phone" value={phoneNo} onChange={(e) => setPhoneNo(e.target.value)} placeholder="9876543210" className="mt-1.5 h-11" />
                    {errors.phone_no && <p className="text-destructive text-xs mt-1">{errors.phone_no}</p>}
                  </div>
                </motion.div>
              )}

              {step === 2 && (
                <motion.div key="step2" variants={stepVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.25 }} className="space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Briefcase size={18} className="text-primary" />
                    <span className="font-display font-semibold text-foreground">Select Your Role</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {([
                      { value: "hr" as const, label: "Recruiter", desc: "I'm hiring talent for my organization", icon: Building2 },
                      { value: "candidate" as const, label: "Candidate", desc: "I'm looking for job opportunities", icon: User },
                    ]).map((r) => (
                      <button
                        key={r.value}
                        type="button"
                        onClick={() => setRole(r.value)}
                        className={`flex flex-col items-center gap-3 p-6 rounded-xl border-2 transition-all duration-200 text-center ${
                          role === r.value
                            ? "border-primary bg-secondary shadow-elevated"
                            : "border-border bg-surface hover:border-primary/30"
                        }`}
                      >
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
                          role === r.value ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                        }`}>
                          <r.icon size={24} />
                        </div>
                        <div>
                          <p className="font-display font-semibold text-foreground">{r.label}</p>
                          <p className="text-xs text-muted-foreground mt-1">{r.desc}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              {step === 3 && role === "hr" && (
                <motion.div key="step3" variants={stepVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.25 }} className="space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Building2 size={18} className="text-primary" />
                    <span className="font-display font-semibold text-foreground">Organization Details</span>
                  </div>
                  <div>
                    <Label htmlFor="orgName">Organization Name</Label>
                    <Input id="orgName" value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="TechCorp" className="mt-1.5 h-11" />
                    {errors.org_name && <p className="text-destructive text-xs mt-1">{errors.org_name}</p>}
                  </div>
                  <div>
                    <Label htmlFor="industry">Industry</Label>
                    <Input id="industry" value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder="Software" className="mt-1.5 h-11" />
                    {errors.industry && <p className="text-destructive text-xs mt-1">{errors.industry}</p>}
                  </div>
                  <div>
                    <Label htmlFor="size">Company Size</Label>
                    <Input id="size" type="number" value={size} onChange={(e) => setSize(e.target.value)} placeholder="500" className="mt-1.5 h-11" />
                    {errors.size && <p className="text-destructive text-xs mt-1">{errors.size}</p>}
                  </div>
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input id="location" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Pune, India" className="mt-1.5 h-11" />
                    {errors.location && <p className="text-destructive text-xs mt-1">{errors.location}</p>}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Navigation buttons */}
            <div className="flex gap-3 mt-8">
              {step > 1 && (
                <Button type="button" variant="outline" onClick={prevStep} className="h-11">
                  <ArrowLeft size={16} className="mr-1" /> Back
                </Button>
              )}
              <Button
                type={step === totalSteps ? "submit" : "button"}
                onClick={step < totalSteps ? nextStep : undefined}
                disabled={isSubmitting}
                className="flex-1 h-11 bg-hero-gradient hover:opacity-90 transition-opacity"
              >
                {isSubmitting
                  ? "Creating..."
                  : (step === totalSteps
                    ? "Create Account"
                    : (step === 2 && role === "candidate" ? "Create Account" : <>Next <ArrowRight size={16} className="ml-1" /></>))}
              </Button>
            </div>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-primary font-medium hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
