import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from "react";
import { questions } from "@/data/questions";

export type AssessmentStep = "landing" | "details" | "assessment" | "results";

interface CandidateDetails {
  fullName: string;
  email: string;
  phone: string;
  jobRole: string;
}

interface AssessmentState {
  step: AssessmentStep;
  candidate: CandidateDetails | null;
  answers: Record<number, number>;
  currentQuestion: number;
  timeRemaining: number;
  submitted: boolean;
  score: number;
  visited: Set<number>;
  markedForReview: Set<number>;
}

interface AssessmentContextType extends AssessmentState {
  setStep: (step: AssessmentStep) => void;
  setCandidate: (details: CandidateDetails) => void;
  selectAnswer: (questionId: number, optionIndex: number) => void;
  goToQuestion: (index: number) => void;
  nextQuestion: () => void;
  prevQuestion: () => void;
  submitTest: () => void;
  startTimer: () => void;
  toggleMarkForReview: (questionId: number) => void;
}

const TIMER_DURATION = 15 * 60; // 15 minutes

const AssessmentContext = createContext<AssessmentContextType | null>(null);

export const useAssessment = () => {
  const ctx = useContext(AssessmentContext);
  if (!ctx) throw new Error("useAssessment must be used within AssessmentProvider");
  return ctx;
};

export const AssessmentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [step, setStep] = useState<AssessmentStep>("landing");
  const [candidate, setCandidate] = useState<CandidateDetails | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(TIMER_DURATION);
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [visited, setVisited] = useState<Set<number>>(new Set());
  const [markedForReview, setMarkedForReview] = useState<Set<number>>(new Set());
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const selectAnswer = useCallback((questionId: number, optionIndex: number) => {
    if (submitted) return;
    setAnswers(prev => ({ ...prev, [questionId]: optionIndex }));
  }, [submitted]);

  const nextQuestion = useCallback(() => {
    setCurrentQuestion(prev => {
      const next = Math.min(prev + 1, questions.length - 1);
      setVisited(v => new Set(v).add(questions[next].id));
      return next;
    });
  }, []);

  const prevQuestion = useCallback(() => {
    setCurrentQuestion(prev => {
      const next = Math.max(prev - 1, 0);
      setVisited(v => new Set(v).add(questions[next].id));
      return next;
    });
  }, []);

  const goToQuestion = useCallback((index: number) => {
    setCurrentQuestion(index);
    setVisited(prev => new Set(prev).add(questions[index].id));
  }, []);

  const toggleMarkForReview = useCallback((questionId: number) => {
    setMarkedForReview(prev => {
      const next = new Set(prev);
      if (next.has(questionId)) next.delete(questionId);
      else next.add(questionId);
      return next;
    });
  }, []);

  const calculateScore = useCallback(() => {
    let correct = 0;
    questions.forEach(q => {
      if (answers[q.id] === q.correctAnswer) correct++;
    });
    return correct;
  }, [answers]);

  const submitTest = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    const finalScore = calculateScore();
    setScore(finalScore);
    setSubmitted(true);
    setStep("results");
  }, [calculateScore]);

  const startTimer = useCallback(() => {
    setTimeRemaining(TIMER_DURATION);
    setVisited(new Set([questions[0].id]));
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  // Auto-submit when timer hits 0
  useEffect(() => {
    if (timeRemaining === 0 && step === "assessment" && !submitted) {
      submitTest();
    }
  }, [timeRemaining, step, submitted, submitTest]);

  // Cleanup timer
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Prevent page refresh during assessment
  useEffect(() => {
    if (step === "assessment" && !submitted) {
      const handler = (e: BeforeUnloadEvent) => {
        e.preventDefault();
        e.returnValue = "";
      };
      window.addEventListener("beforeunload", handler);
      return () => window.removeEventListener("beforeunload", handler);
    }
  }, [step, submitted]);

  return (
    <AssessmentContext.Provider
      value={{
        step, setStep,
        candidate, setCandidate,
        answers, selectAnswer,
        currentQuestion, goToQuestion, nextQuestion, prevQuestion,
        timeRemaining, startTimer,
        submitted, score, submitTest,
        visited, markedForReview, toggleMarkForReview,
      }}
    >
      {children}
    </AssessmentContext.Provider>
  );
};
