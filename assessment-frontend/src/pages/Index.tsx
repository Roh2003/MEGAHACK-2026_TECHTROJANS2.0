import { AssessmentProvider, useAssessment } from "@/context/AssessmentContext";
import LandingSection from "@/components/LandingSection";
import CandidateDetailsForm from "@/components/CandidateDetailsForm";
import AssessmentTest from "@/components/AssessmentTest";
import ResultsSection from "@/components/ResultsSection";

const AssessmentRouter = () => {
  const { step } = useAssessment();

  switch (step) {
    case "landing":
      return <LandingSection />;
    case "details":
      return <CandidateDetailsForm />;
    case "assessment":
      return <AssessmentTest />;
    case "results":
      return <ResultsSection />;
  }
};

const Index = () => (
  <AssessmentProvider>
    <AssessmentRouter />
  </AssessmentProvider>
);

export default Index;
