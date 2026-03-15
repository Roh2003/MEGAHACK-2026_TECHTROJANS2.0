import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import AuthSidePanel from "@/components/AuthSidePanel";
import { motion } from "framer-motion";
import { z } from "zod";
import { toast } from "sonner";
import axios from "axios";
import { apiClient } from "@/lib/axios";
import { Eye, EyeOff } from "lucide-react";

const loginSchema = z.object({
  email: z.string().trim().email("Invalid email").max(255),
  password: z.string().min(1, "Password is required").max(128),
});

const Login = () => {
  const navigate = useNavigate();
  const [tab, setTab] = useState<"recruiter" | "candidate">("recruiter");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = loginSchema.safeParse({ email, password });
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach((err) => { fieldErrors[err.path[0] as string] = err.message; });
      setErrors(fieldErrors);
      return;
    }
    setErrors({});
    setIsLoading(true);
    try {
      const response = await apiClient.post("/auth/login", { email: email.trim(), password });
      const { access_token, user } = response.data.data;
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(user));
      toast.success("Logged in successfully!");
      navigate("/dashboard");
    } catch (error) {
      const message = axios.isAxiosError(error)
        ? (error.response?.data?.message ?? error.response?.data?.detail ?? "Invalid email or password.")
        : "Something went wrong. Please try again.";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
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
              <div className="relative mt-1.5">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="h-11 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-0 flex items-center justify-center w-10 text-muted-foreground hover:text-foreground"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && <p className="text-destructive text-xs mt-1">{errors.password}</p>}
            </div>
            <Button type="submit" disabled={isLoading} className="w-full h-11 bg-hero-gradient hover:opacity-90 transition-opacity">
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 rounded-full border-2 border-primary-foreground/40 border-t-primary-foreground animate-spin" />
                  Signing in...
                </span>
              ) : (
                "Sign In"
              )}
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
