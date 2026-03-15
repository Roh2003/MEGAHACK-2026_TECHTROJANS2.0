import { Link } from "react-router-dom";

const Footer = () => (
  <footer className="border-t border-border bg-surface py-12">
    <div className="container mx-auto px-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
        <div className="col-span-2 md:col-span-1">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-hero-gradient flex items-center justify-center">
              <span className="font-display font-bold text-primary-foreground text-sm">H</span>
            </div>
            <span className="font-display font-bold text-xl text-foreground">HireMind</span>
          </div>
          <p className="text-sm text-muted-foreground">Automate hiring from post to offer with the power of AI.</p>
        </div>
        <div>
          <h4 className="font-display font-semibold text-sm mb-3 text-foreground">Product</h4>
          <div className="flex flex-col gap-2">
            <Link to="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</Link>
            <Link to="/pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Pricing</Link>
          </div>
        </div>
        <div>
          <h4 className="font-display font-semibold text-sm mb-3 text-foreground">Company</h4>
          <div className="flex flex-col gap-2">
            <span className="text-sm text-muted-foreground">About</span>
            <span className="text-sm text-muted-foreground">Careers</span>
          </div>
        </div>
        <div>
          <h4 className="font-display font-semibold text-sm mb-3 text-foreground">Legal</h4>
          <div className="flex flex-col gap-2">
            <span className="text-sm text-muted-foreground">Privacy</span>
            <span className="text-sm text-muted-foreground">Terms</span>
          </div>
        </div>
      </div>
      <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} HireMind. All rights reserved.
      </div>
    </div>
  </footer>
);

export default Footer;
