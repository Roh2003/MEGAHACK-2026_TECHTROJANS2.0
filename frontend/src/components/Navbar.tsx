import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Menu, X } from "lucide-react";

const Navbar = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-surface/80 backdrop-blur-lg border-b border-border">
      <div className="container mx-auto flex items-center justify-between h-16 px-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-hero-gradient flex items-center justify-center">
            <span className="font-display font-bold text-primary-foreground text-sm">H</span>
          </div>
          <span className="font-display font-bold text-xl text-foreground">HireMind</span>
        </Link>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-8">
          <Link to="/" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Features</Link>
          <Link to="/pricing" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Pricing</Link>
          <Link to="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Login</Link>
          <Link to="/register">
            <Button size="sm" className="bg-hero-gradient hover:opacity-90 transition-opacity">Get Started</Button>
          </Link>
        </div>

        {/* Mobile toggle */}
        <button onClick={() => setOpen(!open)} className="md:hidden text-foreground">
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {open && (
        <div className="md:hidden bg-surface border-b border-border px-4 pb-4 flex flex-col gap-3">
          <Link to="/" className="text-sm font-medium text-muted-foreground py-2" onClick={() => setOpen(false)}>Features</Link>
          <Link to="/pricing" className="text-sm font-medium text-muted-foreground py-2" onClick={() => setOpen(false)}>Pricing</Link>
          <Link to="/login" className="text-sm font-medium text-muted-foreground py-2" onClick={() => setOpen(false)}>Login</Link>
          <Link to="/register" onClick={() => setOpen(false)}>
            <Button size="sm" className="w-full bg-hero-gradient">Get Started</Button>
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
