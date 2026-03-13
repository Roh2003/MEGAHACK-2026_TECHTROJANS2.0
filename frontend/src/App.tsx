import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { useLocation } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Dashboard from "./pages/Dashboard.tsx";
import Jobs from "./pages/Jobs.tsx";
import Candidates from "./pages/Candidates.tsx";
import Assessments from "./pages/Assessments.tsx";
import AIInterviews from "./pages/AIInterviews.tsx";
import Offers from "./pages/Offers.tsx";
import History from "./pages/History.tsx";
import Settings from "./pages/Settings.tsx";
import JobProgress from "./pages/JobProgress.tsx";
import CreateJob from "./pages/CreateJob.tsx";
import NotFound from "./pages/NotFound.tsx";
import LandingIndex from "./pages/landing/Index.tsx";
import Login from "./pages/Login.tsx";
import Register from "./pages/Register.tsx";
import AssessmentUpload from "./pages/AssessmentUpload.tsx";
import Pricing from "./pages/landing/Pricing.tsx";

const queryClient = new QueryClient();

const RouteThemeSync = () => {
  const location = useLocation();

  useEffect(() => {
    const landingRoutes = new Set(["/", "/login", "/register"]);
    const isLandingTheme = landingRoutes.has(location.pathname);

    document.body.classList.toggle("theme-landing", isLandingTheme);
    document.body.classList.toggle("theme-dashboard", !isLandingTheme);
  }, [location.pathname]);

  return null;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <RouteThemeSync />
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/" element={<LandingIndex />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />



          <Route path="/jobs" element={<Jobs />} />
          <Route path="/jobs/create" element={<CreateJob />} />
          <Route path="/jobs/:jobId/progress" element={<JobProgress />} />
          <Route path="/candidates" element={<Candidates />} />
          <Route path="/assessments" element={<Assessments />} />
          <Route path="/assessments/upload" element={<AssessmentUpload />} />
          <Route path="/ai-interviews" element={<AIInterviews />} />
          <Route path="/pricing" element={<Pricing />} />

          <Route path="/offers" element={<Offers />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
