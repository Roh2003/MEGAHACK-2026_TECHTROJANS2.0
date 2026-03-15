import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Check } from "lucide-react";
import { motion } from "framer-motion";

const tiers = [
  {
    name: "Starter",
    price: "$49",
    period: "/month",
    description: "For small teams getting started with AI hiring.",
    features: [
      "Up to 5 active job posts",
      "Post to 3 platforms",
      "AI resume scoring (100/month)",
      "Email notifications",
      "Basic candidate ranking",
      "Job post history",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Growth",
    price: "$149",
    period: "/month",
    description: "For growing teams who need the full AI advantage.",
    features: [
      "Up to 25 active job posts",
      "Post to all platforms",
      "Unlimited AI resume scoring",
      "Up to 50 AI voice interviews/month",
      "Custom assessment tests",
      "Talent pool & history search",
      "Offer letter generation",
      "Priority support",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large organizations with advanced needs.",
    features: [
      "Unlimited job posts",
      "All platform integrations",
      "Unlimited AI features",
      "Unlimited AI voice interviews",
      "Custom ML model training",
      "SSO & advanced security",
      "Dedicated account manager",
      "Custom API access",
      "SLA guarantee",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

const Pricing = () => (
  <div className="min-h-screen bg-background">
    <Navbar />
    <section className="pt-32 pb-20 px-4">
      <div className="container mx-auto text-center mb-16">
        <motion.h1
          className="font-display text-4xl md:text-5xl font-extrabold mb-4 text-foreground"
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
        >
          Simple, transparent pricing
        </motion.h1>
        <motion.p
          className="text-lg text-muted-foreground max-w-xl mx-auto"
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.5 }}
        >
          Start free, scale as you grow. No hidden fees.
        </motion.p>
      </div>

      <div className="container mx-auto grid md:grid-cols-3 gap-6 max-w-5xl">
        {tiers.map((tier, i) => (
          <motion.div
            key={tier.name}
            className={`rounded-2xl p-8 border flex flex-col ${
              tier.highlighted
                ? "bg-surface border-primary shadow-elevated relative"
                : "bg-surface border-border shadow-card"
            }`}
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.1, duration: 0.5 }}
          >
            {tier.highlighted && (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-hero-gradient text-primary-foreground text-xs font-semibold">
                Most Popular
              </span>
            )}
            <h3 className="font-display font-bold text-xl text-foreground mb-1">{tier.name}</h3>
            <p className="text-sm text-muted-foreground mb-6">{tier.description}</p>
            <div className="mb-6">
              <span className="text-4xl font-display font-extrabold text-foreground">{tier.price}</span>
              <span className="text-muted-foreground text-sm">{tier.period}</span>
            </div>
            <ul className="flex flex-col gap-3 mb-8 flex-1">
              {tier.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-sm text-foreground">
                  <Check size={16} className="text-accent mt-0.5 shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <Link to="/register">
              <Button
                className={`w-full h-11 ${tier.highlighted ? "bg-hero-gradient hover:opacity-90" : ""}`}
                variant={tier.highlighted ? "default" : "outline"}
              >
                {tier.cta}
              </Button>
            </Link>
          </motion.div>
        ))}
      </div>
    </section>
    <Footer />
  </div>
);

export default Pricing;
