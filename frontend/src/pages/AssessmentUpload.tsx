import { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  ArrowLeft,
  Upload,
  FileText,
  CheckCircle2,
  X,
  AlertCircle,
  FileSpreadsheet,
  FileJson,
  Info,
} from "lucide-react";

type UploadStatus = "idle" | "dragging" | "uploaded" | "error";

interface ParsedQuestion {
  question: string;
  options: string[];
  correctAnswer: string;
}

const ACCEPTED_TYPES: Record<string, { label: string; icon: typeof FileText }> = {
  "application/pdf": { label: "PDF", icon: FileText },
  "text/csv": { label: "CSV", icon: FileSpreadsheet },
  "application/json": { label: "JSON", icon: FileJson },
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
    label: "XLSX",
    icon: FileSpreadsheet,
  },
};

const ACCEPTED_EXTENSIONS = [".pdf", ".csv", ".json", ".xlsx"];
const MAX_FILE_SIZE_MB = 10;

export default function AssessmentUpload() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [previewQuestions, setPreviewQuestions] = useState<ParsedQuestion[]>([]);
  const [previewNote, setPreviewNote] = useState("");

  const validateFile = (f: File): string | null => {
    const ext = "." + f.name.split(".").pop()?.toLowerCase();
    const mimeOrExt = ACCEPTED_TYPES[f.type] || ACCEPTED_EXTENSIONS.includes(ext);
    if (!mimeOrExt) {
      return "Unsupported file type. Please upload a PDF, CSV, JSON, or XLSX file.";
    }
    if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return `File is too large. Maximum allowed size is ${MAX_FILE_SIZE_MB} MB.`;
    }
    return null;
  };

  const normalizeQuestion = (q: Partial<ParsedQuestion>): ParsedQuestion | null => {
    const cleanQuestion = q.question?.trim();
    const cleanOptions = (q.options || []).map((opt) => opt.trim()).filter(Boolean);
    const cleanAnswer = q.correctAnswer?.trim();

    if (!cleanQuestion || cleanOptions.length < 2 || !cleanAnswer) return null;

    return {
      question: cleanQuestion,
      options: cleanOptions,
      correctAnswer: cleanAnswer,
    };
  };

  const parseCsvLine = (line: string): string[] => {
    const cells: string[] = [];
    let current = "";
    let inQuotes = false;

    for (let i = 0; i < line.length; i += 1) {
      const char = line[i];
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i += 1;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === "," && !inQuotes) {
        cells.push(current.trim());
        current = "";
      } else {
        current += char;
      }
    }

    cells.push(current.trim());
    return cells;
  };

  const parseCsvQuestions = (text: string): ParsedQuestion[] => {
    const lines = text
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);

    if (lines.length < 2) return [];

    const headers = parseCsvLine(lines[0]).map((h) => h.toLowerCase());
    const questionIdx = headers.indexOf("question");
    const aIdx = headers.indexOf("option_a");
    const bIdx = headers.indexOf("option_b");
    const cIdx = headers.indexOf("option_c");
    const dIdx = headers.indexOf("option_d");
    const correctIdx = headers.indexOf("correct_answer");

    if ([questionIdx, aIdx, bIdx, cIdx, dIdx, correctIdx].some((idx) => idx === -1)) {
      return [];
    }

    return lines
      .slice(1)
      .map((line) => {
        const cols = parseCsvLine(line);
        return normalizeQuestion({
          question: cols[questionIdx],
          options: [cols[aIdx], cols[bIdx], cols[cIdx], cols[dIdx]],
          correctAnswer: cols[correctIdx],
        });
      })
      .filter((q): q is ParsedQuestion => Boolean(q));
  };

  const parseJsonQuestions = (text: string): ParsedQuestion[] => {
    const parsed = JSON.parse(text);
    const list = Array.isArray(parsed) ? parsed : [];

    return list
      .map((item: unknown) => {
        if (!item || typeof item !== "object") return null;
        const obj = item as Record<string, unknown>;

        const options = Array.isArray(obj.options)
          ? obj.options.map((opt) => String(opt))
          : [obj.option_a, obj.option_b, obj.option_c, obj.option_d]
              .filter(Boolean)
              .map((opt) => String(opt));

        const correctByIndex =
          typeof obj.correct === "number" && options[obj.correct]
            ? options[obj.correct]
            : undefined;

        return normalizeQuestion({
          question: typeof obj.question === "string" ? obj.question : "",
          options,
          correctAnswer:
            typeof obj.correct_answer === "string"
              ? obj.correct_answer
              : typeof obj.answer === "string"
              ? obj.answer
              : correctByIndex || "",
        });
      })
      .filter((q): q is ParsedQuestion => Boolean(q));
  };

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const f = files[0];
    const err = validateFile(f);
    if (err) {
      setFile(null);
      setPreviewQuestions([]);
      setPreviewNote("");
      setErrorMsg(err);
      setStatus("error");
      return;
    }

    const ext = "." + f.name.split(".").pop()?.toLowerCase();
    let parsedQuestions: ParsedQuestion[] = [];
    let nextPreviewNote = "";

    try {
      if (ext === ".csv") {
        parsedQuestions = parseCsvQuestions(await f.text());
      } else if (ext === ".json") {
        parsedQuestions = parseJsonQuestions(await f.text());
      } else {
        nextPreviewNote = "Preview is currently available for CSV and JSON files. PDF/XLSX will be validated after upload.";
      }
    } catch {
      setFile(null);
      setPreviewQuestions([]);
      setPreviewNote("");
      setErrorMsg("Unable to read the selected file. Please verify its format and try again.");
      setStatus("error");
      return;
    }

    if ((ext === ".csv" || ext === ".json") && parsedQuestions.length === 0) {
      setFile(null);
      setPreviewQuestions([]);
      setPreviewNote("");
      setErrorMsg("No valid questions found. Please check your file columns and answer format.");
      setStatus("error");
      return;
    }

    setFile(f);
    setPreviewQuestions(parsedQuestions.slice(0, 5));
    setPreviewNote(nextPreviewNote);
    setErrorMsg("");
    setStatus("uploaded");
  }, []);

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setStatus("dragging");
  };

  const onDragLeave = () => {
    setStatus((s) => (s === "dragging" ? "idle" : s));
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    void handleFiles(e.dataTransfer.files);
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    void handleFiles(e.target.files);
    e.target.value = "";
  };

  const removeFile = () => {
    setFile(null);
    setPreviewQuestions([]);
    setPreviewNote("");
    setStatus("idle");
    setErrorMsg("");
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    await new Promise((res) => setTimeout(res, 1500));
    setIsUploading(false);
    navigate("/assessments");
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const highlightBorder =
    status === "dragging"
      ? "border-primary bg-primary/5"
      : status === "error"
      ? "border-destructive bg-destructive/5"
      : status === "uploaded"
      ? "border-success bg-success/5"
      : "border-border hover:border-primary/50 hover:bg-muted/30";

  return (
    <DashboardLayout title="Upload Question Paper">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)} className="shrink-0">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="font-display text-xl font-bold text-foreground">Assessment Upload</h2>
            <p className="text-sm text-muted-foreground">
              Upload your MCQ question paper - candidates will be assessed automatically.
            </p>
          </div>
        </div>

        <Card className="border-border/50">
          <CardContent className="p-4 flex gap-3">
            <Info className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <div className="space-y-1 text-sm text-muted-foreground">
              <p className="font-medium text-foreground">Supported formats</p>
              <ul className="list-disc list-inside space-y-0.5">
                <li>
                  <span className="font-medium text-foreground">PDF</span> - question + A/B/C/D options + check mark on correct answer
                </li>
                <li>
                  <span className="font-medium text-foreground">CSV / XLSX</span> - columns:{" "}
                  <code className="text-xs bg-muted px-1 py-0.5 rounded">
                    question, option_a, option_b, option_c, option_d, correct_answer
                  </code>
                </li>
                <li>
                  <span className="font-medium text-foreground">JSON</span> - array of{" "}
                  <code className="text-xs bg-muted px-1 py-0.5 rounded">
                    {"{ question, options: [], correct: 0 }"}
                  </code>
                </li>
              </ul>
              <p className="text-xs pt-1">Max file size: {MAX_FILE_SIZE_MB} MB</p>
            </div>
          </CardContent>
        </Card>

        <div
          className={`relative rounded-2xl border-2 border-dashed transition-all duration-200 cursor-pointer ${highlightBorder}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => !file && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED_EXTENSIONS.join(",")}
            className="sr-only"
            onChange={onInputChange}
            aria-label="Upload question paper"
          />

          {status === "uploaded" && file ? (
            <div className="flex items-center gap-4 p-6">
              <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-success/10 shrink-0">
                <CheckCircle2 className="h-7 w-7 text-success" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-foreground truncate">{file.name}</p>
                <p className="text-sm text-muted-foreground">{formatBytes(file.size)}</p>
                <Badge variant="outline" className="mt-1 text-xs text-success border-success/30">
                  Ready to upload
                </Badge>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                }}
                className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors shrink-0"
                aria-label="Remove file"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : status === "error" ? (
            <div className="flex flex-col items-center justify-center gap-3 p-10 text-center">
              <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-destructive/10">
                <AlertCircle className="h-7 w-7 text-destructive" />
              </div>
              <p className="font-semibold text-destructive">Upload failed</p>
              <p className="text-sm text-muted-foreground max-w-xs">{errorMsg}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                  inputRef.current?.click();
                }}
              >
                Try Again
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-4 p-14 text-center select-none">
              <div
                className={`flex items-center justify-center w-16 h-16 rounded-2xl transition-colors ${
                  status === "dragging" ? "bg-primary/20" : "bg-muted"
                }`}
              >
                <Upload
                  className={`h-7 w-7 transition-colors ${
                    status === "dragging" ? "text-primary" : "text-muted-foreground"
                  }`}
                />
              </div>
              <div>
                <p className="font-semibold text-foreground text-base">
                  {status === "dragging"
                    ? "Drop your file here"
                    : "Drag and drop your question paper"}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  or{" "}
                  <span className="text-primary font-medium underline underline-offset-2 cursor-pointer">
                    browse files
                  </span>
                </p>
              </div>
              <div className="flex items-center gap-2 flex-wrap justify-center">
                {Object.values(ACCEPTED_TYPES).map(({ label }) => (
                  <Badge key={label} variant="outline" className="text-xs">
                    {label}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {(previewQuestions.length > 0 || previewNote) && (
          <Card className="border-border/50">
            <CardContent className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-display text-base font-semibold text-foreground">Question Preview</h3>
                {previewQuestions.length > 0 && (
                  <Badge variant="outline" className="text-xs">
                    Showing {previewQuestions.length} questions
                  </Badge>
                )}
              </div>

              {previewNote && (
                <div className="rounded-lg border border-primary/20 bg-primary/5 px-3 py-2 text-xs text-primary">
                  {previewNote}
                </div>
              )}

              {previewQuestions.length > 0 && (
                <div className="space-y-3">
                  {previewQuestions.map((q, index) => (
                    <div key={`${q.question}-${index}`} className="rounded-xl border border-border/60 bg-card p-4">
                      <p className="text-sm font-medium text-foreground">
                        Q{index + 1}. {q.question}
                      </p>
                      <div className="mt-3 grid gap-2 sm:grid-cols-2">
                        {q.options.map((opt, optIndex) => {
                          const isCorrect = opt.trim().toLowerCase() === q.correctAnswer.trim().toLowerCase();
                          return (
                            <div
                              key={`${opt}-${optIndex}`}
                              className={`rounded-md border px-3 py-2 text-xs ${
                                isCorrect
                                  ? "border-success/30 bg-success/10 text-success"
                                  : "border-border/60 bg-muted/40 text-muted-foreground"
                              }`}
                            >
                              <span className="font-semibold mr-1">{String.fromCharCode(65 + optIndex)}.</span>
                              {opt}
                              {isCorrect && <span className="ml-2 font-semibold">(Correct)</span>}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={() => navigate(-1)} disabled={isUploading}>
            Cancel
          </Button>
          <Button
            disabled={status !== "uploaded" || isUploading}
            onClick={handleUpload}
            className="min-w-32"
          >
            {isUploading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 rounded-full border-2 border-primary-foreground/40 border-t-primary-foreground animate-spin" />
                Uploading...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Upload className="h-4 w-4" />
                Upload and Continue
              </span>
            )}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}
