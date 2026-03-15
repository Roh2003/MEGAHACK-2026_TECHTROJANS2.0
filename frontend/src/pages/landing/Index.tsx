import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, Globe, Brain, Mic, CheckCircle, ArrowRight, BarChart3, Mail, Users } from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.5 } }),
};

const features = [
  {
    icon: Globe,
    title: "Multi-Platform Job Posting",
    description: "Post once, publish everywhere. Your job listings automatically go live on LinkedIn, Naukri, Indeed and more — saving hours of repetitive work.",
  },
  {
    icon: Brain,
    title: "AI Resume Scoring",
    description: "Our ML model analyzes every resume against your JD, assigns a match score out of 100, and provides clear reasons for every decision.",
  },
  {
    icon: Mic,
    title: "AI Voice Interviews",
    description: "An AI interviewer conducts voice interviews, evaluates answers in real-time, and generates comprehensive performance summaries.",
  },
  {
    icon: Mail,
    title: "Automated Communication",
    description: "Every candidate gets timely email updates with selection status and rejection reasons — no manual follow-ups needed.",
  },
  {
    icon: BarChart3,
    title: "Smart Candidate Ranking",
    description: "Candidates are ranked by AI scores across rounds. HR picks the top performers with full transparency into every score.",
  },
  {
    icon: Users,
    title: "Talent Pool & History",
    description: "All past candidates are saved. When a new role opens, our system suggests the best matches from your historical talent pool.",
  },
];

const steps = [
  { step: "01", title: "Post Your Job", desc: "Define the role, set timelines, and publish. We distribute it across all major platforms instantly." },
  { step: "02", title: "AI Screens Resumes", desc: "Our model reads every application, scores them against your JD, and ranks candidates automatically." },
  { step: "03", title: "Conduct Rounds", desc: "Create assessments, schedule AI voice interviews, or set up face-to-face meetings — all from one dashboard." },
  { step: "04", title: "Hire the Best", desc: "Select top candidates, generate offer letters, and close positions. Every step is tracked and documented." },
];

const LandingIndex = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="pt-32 pb-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-40" />
        <div className="container mx-auto text-center relative z-10">
          <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={0}>
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Sparkles size={14} /> AI-Powered Recruitment Platform
            </span>
          </motion.div>
          <motion.h1
            className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 max-w-4xl mx-auto"
            initial="hidden" animate="visible" variants={fadeUp} custom={1}
          >
            Automate hiring from{" "}
            <span className="text-gradient">post to offer</span>
          </motion.h1>
          <motion.p
            className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10"
            initial="hidden" animate="visible" variants={fadeUp} custom={2}
          >
            Post jobs across platforms, screen resumes with AI, conduct voice interviews, and hire top talent — all from one intelligent dashboard.
          </motion.p>
          <motion.div className="flex flex-col sm:flex-row gap-4 justify-center" initial="hidden" animate="visible" variants={fadeUp} custom={3}>
            <Link to="/register">
              <Button size="lg" className="bg-hero-gradient hover:opacity-90 transition-opacity text-base px-8 h-12 shadow-glow">
                Start Hiring Free <ArrowRight size={16} className="ml-2" />
              </Button>
            </Link>
            <Link to="/pricing">
              <Button size="lg" variant="outline" className="text-base px-8 h-12">
                View Pricing
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Abstract dashboard mockup */}
        <motion.div
          className="container mx-auto mt-16 relative z-10"
          initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5, duration: 0.7 }}
        >
          <div className="bg-surface rounded-2xl shadow-elevated border border-border p-6 md:p-8 max-w-5xl mx-auto">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-3 h-3 rounded-full bg-destructive/60" />
              <div className="w-3 h-3 rounded-full bg-accent/60" />
              <div className="w-3 h-3 rounded-full bg-primary/40" />
              <span className="ml-4 text-xs text-muted-foreground font-mono">HireMind Dashboard</span>
            </div>
            <div className="grid grid-cols-3 gap-4 mb-4">
              {["Active Jobs", "Applications", "AI Interviews"].map((label, i) => (
                <div key={label} className="bg-background rounded-xl p-4 border border-border">
                  <p className="text-xs text-muted-foreground mb-1">{label}</p>
                  <p className="text-2xl font-display font-bold text-foreground">{[12, 348, 24][i]}</p>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-5 gap-3">
              {[92, 87, 81, 76, 69].map((score, i) => (
                <div key={i} className="bg-background rounded-lg p-3 border border-border text-center">
                  <div className="w-8 h-8 rounded-full bg-muted mx-auto mb-2" />
                  <div className="text-xs text-muted-foreground mb-1">Candidate {i + 1}</div>
                  <span className={`text-sm font-bold ${score >= 80 ? 'text-accent' : 'text-muted-foreground'}`}>{score}%</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4 text-foreground">Everything you need to hire smarter</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">From job posting to offer letter, every step is powered by AI and built for efficiency.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                className="bg-surface rounded-2xl p-6 border border-border shadow-card hover:shadow-elevated transition-shadow duration-300 group"
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.08, duration: 0.4 }}
              >
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-hero-gradient group-hover:text-primary-foreground transition-all duration-300">
                  <f.icon size={20} className="text-primary group-hover:text-primary-foreground transition-colors" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-2 text-foreground">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4 bg-surface">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4 text-foreground">How it works</h2>
            <p className="text-muted-foreground text-lg">Four simple steps to transform your hiring process.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {steps.map((s, i) => (
              <motion.div
                key={s.step}
                className="relative"
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.12, duration: 0.4 }}
              >
                <span className="text-6xl font-display font-extrabold text-primary/10 mb-2 block">{s.step}</span>
                <h3 className="font-display font-semibold text-lg mb-2 text-foreground">{s.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="bg-hero-gradient rounded-3xl p-10 md:p-16 text-center max-w-4xl mx-auto relative overflow-hidden">
            <div className="absolute inset-0 bg-grid opacity-10" />
            <div className="relative z-10">
              <h2 className="font-display text-3xl md:text-4xl font-bold text-primary-foreground mb-4">Ready to revolutionize your hiring?</h2>
              <p className="text-primary-foreground/80 text-lg mb-8 max-w-xl mx-auto">Join thousands of HR teams who've cut hiring time by 70% with AI-powered recruitment.</p>
              <Link to="/register">
                <Button size="lg" className="bg-surface text-foreground hover:bg-surface/90 text-base px-8 h-12 font-semibold">
                  Get Started Free <ArrowRight size={16} className="ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default LandingIndex;
