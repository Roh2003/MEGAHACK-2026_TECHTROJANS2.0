import { Sparkles, BarChart3, Mic } from "lucide-react";

const AuthSidePanel = () => (
  <div className="hidden lg:flex flex-col justify-center items-center bg-hero-gradient p-12 relative overflow-hidden">
    <div className="absolute inset-0 bg-grid opacity-10" />
    <div className="relative z-10 max-w-md text-center">
      <div className="w-14 h-14 rounded-2xl bg-primary-foreground/20 backdrop-blur-sm flex items-center justify-center mx-auto mb-8">
        <Sparkles size={28} className="text-primary-foreground" />
      </div>
      <h2 className="font-display text-3xl font-bold text-primary-foreground mb-4">
        Hire smarter, not harder
      </h2>
      <p className="text-primary-foreground/80 text-base leading-relaxed mb-10">
        Join 2,000+ companies using AI to find the perfect candidates in half the time.
      </p>
      <div className="space-y-4 text-left">
        {[
          { icon: BarChart3, text: "AI scores every resume against your JD" },
          { icon: Mic, text: "Voice interviews conducted by AI" },
          { icon: Sparkles, text: "Auto-post to LinkedIn, Naukri & more" },
        ].map(({ icon: Icon, text }) => (
          <div key={text} className="flex items-center gap-3 bg-primary-foreground/10 rounded-xl p-3 backdrop-blur-sm">
            <Icon size={18} className="text-primary-foreground shrink-0" />
            <span className="text-sm text-primary-foreground/90">{text}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

export default AuthSidePanel;
