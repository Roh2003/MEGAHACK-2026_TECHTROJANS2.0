import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
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

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/jobs/create" element={<CreateJob />} />
          <Route path="/jobs/:jobId/progress" element={<JobProgress />} />
          <Route path="/candidates" element={<Candidates />} />
          <Route path="/assessments" element={<Assessments />} />
          <Route path="/ai-interviews" element={<AIInterviews />} />
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
