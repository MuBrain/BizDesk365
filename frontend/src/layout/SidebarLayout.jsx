import { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  LayoutDashboard, 
  ShieldCheck, 
  Brain, 
  Bot, 
  Settings, 
  Zap,
  LogOut,
  Bell,
  Search,
  Menu,
  X,
  ChevronRight
} from "lucide-react";

const iconMap = {
  LayoutDashboard: LayoutDashboard,
  ShieldCheck: ShieldCheck,
  Brain: Brain,
  Bot: Bot,
  Settings: Settings,
  Zap: Zap,
};

const getIcon = (iconName) => {
  return iconMap[iconName] || LayoutDashboard;
};

export default function SidebarLayout() {
  const { user, modules, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Build nav items from modules
  const navItems = [
    { id: "home", label: "Accueil", path: "/dashboards", icon: LayoutDashboard },
    ...modules.flatMap(mod => 
      mod.nav_items.map(item => ({
        id: item.id,
        label: item.label,
        path: item.path,
        icon: getIcon(item.icon),
        disabled: !mod.enabled,
        moduleName: mod.name
      }))
    )
  ];

  // Separate settings from other nav items
  const mainNavItems = navItems.filter(item => item.path !== "/settings");
  const settingsItem = navItems.find(item => item.path === "/settings");

  return (
    <div className="min-h-screen bg-slate-50 flex" data-testid="sidebar-layout">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 bg-slate-900 
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        data-testid="sidebar"
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-semibold text-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Bizdesk365
              </span>
            </div>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <ScrollArea className="flex-1 py-4">
            <nav className="px-3 space-y-1">
              {mainNavItems.map((item) => (
                <NavLink
                  key={item.id}
                  to={item.disabled ? "#" : item.path}
                  onClick={(e) => item.disabled && e.preventDefault()}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-3 py-2.5 rounded-lg
                    text-sm font-medium transition-colors duration-150
                    ${item.disabled 
                      ? 'text-slate-600 cursor-not-allowed' 
                      : isActive 
                        ? 'bg-slate-800 text-white border-l-4 border-blue-500 -ml-[4px] pl-[calc(0.75rem+4px)]' 
                        : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                    }
                  `}
                  data-testid={`nav-${item.id}`}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  <span className="truncate">{item.label}</span>
                  {item.disabled && (
                    <span className="ml-auto text-xs bg-slate-700 px-2 py-0.5 rounded text-slate-400">
                      Bientôt
                    </span>
                  )}
                </NavLink>
              ))}
            </nav>
          </ScrollArea>

          {/* Settings & User section */}
          <div className="border-t border-slate-800 p-3 space-y-2">
            {settingsItem && (
              <NavLink
                to={settingsItem.path}
                className={({ isActive }) => `
                  flex items-center gap-3 px-3 py-2.5 rounded-lg
                  text-sm font-medium transition-colors duration-150
                  ${isActive 
                    ? 'bg-slate-800 text-white' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }
                `}
                data-testid="nav-settings"
              >
                <Settings className="w-5 h-5" />
                <span>Paramètres</span>
              </NavLink>
            )}
            
            {/* User info */}
            <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-800/50">
              <Avatar className="w-8 h-8">
                <AvatarImage src="https://images.unsplash.com/photo-1689600944138-da3b150d9cb8?w=100" />
                <AvatarFallback className="bg-blue-600 text-white text-sm">
                  {user?.email?.charAt(0).toUpperCase() || "U"}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.email || "Utilisateur"}
                </p>
                <p className="text-xs text-slate-500 truncate">
                  Demo Org
                </p>
              </div>
              <button 
                onClick={handleLogout}
                className="p-1.5 text-slate-400 hover:text-white transition-colors"
                title="Déconnexion"
                data-testid="logout-btn"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header */}
        <header className="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-4 lg:px-6 sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 -ml-2 text-slate-600 hover:text-slate-900"
            >
              <Menu className="w-5 h-5" />
            </button>
            
            {/* Search */}
            <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg w-64">
              <Search className="w-4 h-4 text-slate-400" />
              <input 
                type="text"
                placeholder="Rechercher..."
                className="bg-transparent border-none outline-none text-sm text-slate-700 placeholder:text-slate-400 w-full"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Notifications */}
            <button className="relative p-2 text-slate-500 hover:text-slate-700 transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* User dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2 hover:bg-slate-100">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src="https://images.unsplash.com/photo-1689600944138-da3b150d9cb8?w=100" />
                    <AvatarFallback className="bg-blue-600 text-white text-sm">
                      {user?.email?.charAt(0).toUpperCase() || "U"}
                    </AvatarFallback>
                  </Avatar>
                  <ChevronRight className="w-4 h-4 text-slate-400 rotate-90" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span>{user?.email}</span>
                    <span className="font-normal text-xs text-slate-500">Tenant: Demo Org</span>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="w-4 h-4 mr-2" />
                  Déconnexion
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
