import {
  LayoutDashboard,
  Briefcase,
  Users,
  ClipboardList,
  History,
  Settings,
  Bot,
  FileText,
  LogOut,
} from "lucide-react";
import { useMemo } from "react";
import { NavLink } from "@/components/NavLink";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "./ui/button";

const mainItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  // { title: "", url: "/dashboard", icon: LayoutDashboard },

  { title: "Job Posts", url: "/jobs", icon: Briefcase },
  { title: "Candidates", url: "/candidates", icon: Users },
  { title: "Assessments", url: "/assessments", icon: ClipboardList },
  { title: "AI Interviews", url: "/ai-interviews", icon: Bot },
];

// const secondaryItems = [
//   { title: "Offer Letters", url: "/offers", icon: FileText },
//   { title: "History", url: "/history", icon: History },
//   { title: "Settings", url: "/settings", icon: Settings },
// ];

interface SidebarUser {
  name?: string;
  role?: string;
}

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();
  const currentPath = location.pathname;
  const navigate = useNavigate();

  const sidebarUser = useMemo<Required<SidebarUser>>(() => {
    try {
      const rawUser = localStorage.getItem("user");
      if (!rawUser) {
        return { name: "Guest User", role: "Recruiter" };
      }

      const parsedUser = JSON.parse(rawUser) as SidebarUser;
      return {
        name: parsedUser.name?.trim() || "Guest User",
        role: parsedUser.role?.trim() || "Recruiter",
      };
    } catch {
      return { name: "Guest User", role: "Recruiter" };
    }
  }, []);

  const roleLabel = sidebarUser.role
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());

  const initials = sidebarUser.name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("") || "HR";

  const isActive = (path: string) =>
    path === "/" ? currentPath === "/" : currentPath.startsWith(path);

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="p-4 border-b bg-gray-900 border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-sidebar-primary flex items-center justify-center shrink-0">
            <Briefcase className="h-5 w-5 text-sidebar-primary-foreground" />
          </div>
          {!collapsed && (
            <div>
              <h2 className="font-display text-base font-bold text-sidebar-primary-foreground tracking-tight">
                HireMind
              </h2>
              <p className="text-xs text-sidebar-foreground/60">Recruitment Platform</p>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent className="bg-gray-900">
        <SidebarGroup>
          {/* <SidebarGroupLabel className="text-sidebar-foreground/50 text-xs uppercase tracking-wider">
            Main
          </SidebarGroupLabel> */}
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={isActive(item.url)}>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className="hover:bg-sidebar-accent"
                      activeClassName="bg-sidebar-accent text-sidebar-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/50 text-xs uppercase tracking-wider">
            Manage
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {secondaryItems && secondaryItems?.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={isActive(item.url)}>
                    <NavLink
                      to={item.url}
                      className="hover:bg-sidebar-accent"
                      activeClassName="bg-sidebar-accent text-sidebar-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup> */}
      </SidebarContent>

      <SidebarFooter className="p-4 border-t border-sidebar-border  ">
        <div className="flex justify-between items-center w-full gap-3">
          <div className="flex items-center gap-2">

          <div className="h-8 w-8 rounded-full bg-sidebar-primary/20 flex items-center justify-center shrink-0">
            <span className="text-sm font-semibold text-sidebar-primary">{initials}</span>
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm font-medium text-sidebar-accent-foreground truncate">
                {sidebarUser.name}
              </p>
              <p className="text-xs text-sidebar-foreground/50 truncate">{roleLabel}</p>
            </div>
          )}
        <div>
          </div>
        </div>
          <Button size="icon" onClick={()=>{navigate("/login"); localStorage.clear()}}><LogOut/></Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
