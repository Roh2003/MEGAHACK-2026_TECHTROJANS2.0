import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import AuthSidePanel from "@/components/AuthSidePanel";
import { motion } from "framer-motion";
import { z } from "zod";
import { toast } from "sonner";

const loginSchema = z.object({
  email: z.string().trim().email("Invalid email").max(255),
  password: z.string().min(1, "Password is required").max(128),
});

const Login = () => {
  const [tab, setTab] = useState<"recruiter" | "candidate">("recruiter");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const result = loginSchema.safeParse({ email, password });
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach((err) => { fieldErrors[err.path[0] as string] = err.message; });
      setErrors(fieldErrors);
      return;
    }
    setErrors({});
    toast.success(`Logged in as ${tab}`);
    // API call with { email, password, role: tab }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <AuthSidePanel />
      <div className="flex items-center justify-center p-6 sm:p-8 bg-background">
        <motion.div
          className="w-full max-w-md"
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}
        >
          <Link to="/" className="flex items-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-lg bg-hero-gradient flex items-center justify-center">
              <span className="font-display font-bold text-primary-foreground text-sm">H</span>
            </div>
            <span className="font-display font-bold text-xl text-foreground">HireMind</span>
          </Link>

          <h1 className="font-display text-2xl font-bold text-foreground mb-1">Welcome back</h1>
          <p className="text-muted-foreground text-sm mb-6">Sign in to your account to continue.</p>

          {/* Role tabs */}
          {/* <div className="flex items-center bg-muted rounded-full p-1 mb-6">
            <button
              onClick={() => setTab("recruiter")}
              className={`flex-1 text-sm font-medium py-2.5 px-4 rounded-full transition-all duration-200 ${
                tab === "recruiter" ? "bg-surface text-foreground shadow-card" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Recruiter
            </button>
            <button
              onClick={() => setTab("candidate")}
              className={`flex-1 text-sm font-medium py-2.5 px-4 rounded-full transition-all duration-200 ${
                tab === "candidate" ? "bg-surface text-foreground shadow-card" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Candidate
            </button>
          </div> */}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder={tab === "recruiter" ? "rohit@techcorp.com" : "candidate@email.com"}
                className="mt-1.5 h-11"
              />
              {errors.email && <p className="text-destructive text-xs mt-1">{errors.email}</p>}
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••" className="mt-1.5 h-11"
              />
              {errors.password && <p className="text-destructive text-xs mt-1">{errors.password}</p>}
            </div>
            <Button type="submit" className="w-full h-11 bg-hero-gradient hover:opacity-90 transition-opacity">
              Sign In as {tab === "recruiter" ? "Recruiter" : "Candidate"}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Don't have an account?{" "}
            <Link to="/register" className="text-primary font-medium hover:underline">Create one</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
