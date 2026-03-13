import { useAssessment } from "@/context/AssessmentContext";
import { questions } from "@/data/questions";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, ArrowRight, Send, Clock, AlertTriangle, Bookmark, CheckCircle2, Circle, Eye, Flag } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { cn } from "@/lib/utils";

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
};

const AssessmentTest = () => {
  const {
    currentQuestion, answers, selectAnswer,
    nextQuestion, prevQuestion, goToQuestion,
    timeRemaining, submitTest, candidate,
    visited, markedForReview, toggleMarkForReview,
  } = useAssessment();

  const q = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const answeredCount = Object.keys(answers).length;
  const isLowTime = timeRemaining <= 60;

  const visitedCount = visited.size;
  const markedCount = markedForReview.size;
  const unattemptedCount = questions.length - answeredCount;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="sticky top-0 z-10 border-b bg-card/80 backdrop-blur-md px-4 py-3">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <div className="text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">{candidate?.fullName}</span>
            <span className="hidden sm:inline"> · {candidate?.jobRole}</span>
          </div>
          <div className={cn(
            "flex items-center gap-1.5 font-mono text-sm font-bold px-3 py-1.5 rounded-lg",
            isLowTime ? "bg-destructive/10 text-destructive animate-pulse" : "bg-muted text-foreground"
          )}>
            <Clock className="h-4 w-4" />
            {formatTime(timeRemaining)}
          </div>
        </div>
      </header>

      {/* Stats bar with distinct colors */}
      <div className="border-b bg-card px-4 py-3">
        <div className="max-w-5xl mx-auto flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-xs font-medium">
          <div className="flex items-center gap-2 bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-lg">
            <CheckCircle2 className="h-4 w-4 text-primary" />
            <span className="text-primary font-bold">{answeredCount}</span>
            <span className="text-primary/70">Attempted</span>
          </div>
          <div className="flex items-center gap-2 bg-accent/10 border border-accent/20 px-3 py-1.5 rounded-lg">
            <Eye className="h-4 w-4 text-accent" />
            <span className="text-accent font-bold">{visitedCount}</span>
            <span className="text-accent/70">Visited</span>
          </div>
          <div className="flex items-center gap-2 bg-warning/10 border border-warning/20 px-3 py-1.5 rounded-lg">
            <Flag className="h-4 w-4 text-warning" />
            <span className="text-warning font-bold">{markedCount}</span>
            <span className="text-warning/70">Marked</span>
          </div>
          <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/20 px-3 py-1.5 rounded-lg">
            <Circle className="h-4 w-4 text-destructive" />
            <span className="text-destructive font-bold">{unattemptedCount}</span>
            <span className="text-destructive/70">Unattempted</span>
          </div>
        </div>
      </div>

      <div className="flex-1 px-4 py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Question {currentQuestion + 1} of {questions.length}</span>
              <span>{answeredCount} of {questions.length} answered</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Question card */}
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6 sm:p-8 space-y-6">
              <div className="flex items-start justify-between gap-3">
                <h2 className="text-lg sm:text-xl font-semibold text-card-foreground leading-relaxed">
                  {q.question}
                </h2>
                <button
                  onClick={() => toggleMarkForReview(q.id)}
                  className={cn(
                    "shrink-0 p-2 rounded-lg transition-colors",
                    markedForReview.has(q.id)
                      ? "bg-warning/20 text-warning"
                      : "text-muted-foreground hover:bg-muted"
                  )}
                  title={markedForReview.has(q.id) ? "Unmark for review" : "Mark for review"}
                >
                  <Bookmark className={cn("h-5 w-5", markedForReview.has(q.id) && "fill-current")} />
                </button>
              </div>

              <div className="space-y-3">
                {q.options.map((option, idx) => {
                  const isSelected = answers[q.id] === idx;
                  return (
                    <button
                      key={idx}
                      onClick={() => selectAnswer(q.id, idx)}
                      className={cn(
                        "w-full text-left p-4 rounded-xl border-2 transition-all duration-150 text-sm sm:text-base",
                        isSelected
                          ? "border-primary bg-primary/5 font-medium"
                          : "border-border hover:border-primary/40 hover:bg-muted/50"
                      )}
                    >
                      <span className={cn(
                        "inline-flex items-center justify-center h-6 w-6 rounded-full text-xs font-bold mr-3",
                        isSelected ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                      )}>
                        {String.fromCharCode(65 + idx)}
                      </span>
                      {option}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Question dots */}
          <div className="flex flex-wrap gap-2 justify-center">
            {questions.map((question, idx) => (
              <button
                key={question.id}
                onClick={() => goToQuestion(idx)}
                className={cn(
                  "h-8 w-8 rounded-lg text-xs font-semibold transition-all relative",
                  idx === currentQuestion
                    ? "bg-primary text-primary-foreground ring-2 ring-primary/30"
                    : answers[question.id] !== undefined
                    ? "bg-accent text-accent-foreground"
                    : visited.has(question.id)
                    ? "bg-secondary text-secondary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                )}
              >
                {idx + 1}
                {markedForReview.has(question.id) && (
                  <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-warning border-2 border-card" />
                )}
              </button>
            ))}
          </div>

          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-4 text-[11px] text-muted-foreground">
            <span className="flex items-center gap-1.5"><span className="h-3 w-3 rounded bg-primary" /> Current</span>
            <span className="flex items-center gap-1.5"><span className="h-3 w-3 rounded bg-accent" /> Answered</span>
            <span className="flex items-center gap-1.5"><span className="h-3 w-3 rounded bg-secondary" /> Visited</span>
            <span className="flex items-center gap-1.5"><span className="h-3 w-3 rounded bg-muted" /> Not Visited</span>
            <span className="flex items-center gap-1.5"><span className="h-3 w-3 rounded bg-warning relative"><span className="absolute -top-0.5 -right-0.5 h-1.5 w-1.5 rounded-full bg-warning" /></span> Marked</span>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between gap-3">
            <Button
              variant="outline"
              onClick={prevQuestion}
              disabled={currentQuestion === 0}
              className="rounded-xl"
            >
              <ArrowLeft className="h-4 w-4 mr-1" /> Previous
            </Button>

            {currentQuestion < questions.length - 1 ? (
              <Button onClick={nextQuestion} className="rounded-xl">
                Next <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button className="rounded-xl bg-accent hover:bg-accent/90 text-accent-foreground">
                    <Send className="h-4 w-4 mr-1" /> Submit Test
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent className="max-w-md">
                  <AlertDialogHeader>
                    <AlertDialogTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5 text-destructive" />
                      Submit Assessment?
                    </AlertDialogTitle>
                    <AlertDialogDescription asChild>
                      <div className="space-y-3">
                        <p>Please review your attempt summary before submitting:</p>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="flex items-center gap-2 bg-primary/10 rounded-lg px-3 py-2">
                            <CheckCircle2 className="h-4 w-4 text-primary" />
                            <span><strong>{answeredCount}</strong> Attempted</span>
                          </div>
                          <div className="flex items-center gap-2 bg-destructive/10 rounded-lg px-3 py-2">
                            <Circle className="h-4 w-4 text-destructive" />
                            <span><strong>{unattemptedCount}</strong> Unattempted</span>
                          </div>
                          <div className="flex items-center gap-2 bg-warning/10 rounded-lg px-3 py-2">
                            <Flag className="h-4 w-4 text-warning" />
                            <span><strong>{markedCount}</strong> Marked</span>
                          </div>
                          <div className="flex items-center gap-2 bg-accent/10 rounded-lg px-3 py-2">
                            <Eye className="h-4 w-4 text-accent" />
                            <span><strong>{visitedCount}</strong> Visited</span>
                          </div>
                        </div>
                        {unattemptedCount > 0 && (
                          <p className="text-destructive text-xs font-medium">
                            ⚠ You have {unattemptedCount} unanswered question(s).
                          </p>
                        )}
                        {markedCount > 0 && (
                          <p className="text-warning text-xs font-medium">
                            ⚠ You have {markedCount} question(s) marked for review.
                          </p>
                        )}
                        <p className="text-xs">This action cannot be undone.</p>
                      </div>
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Review Answers</AlertDialogCancel>
                    <AlertDialogAction onClick={submitTest}>Confirm Submit</AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessmentTest;
