import { useEffect, useState, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

// Pages
import LoginPage from "@/pages/LoginPage";
import DashboardHome from "@/pages/DashboardHome";
import ComplianceOverview from "@/pages/ComplianceOverview";
import EnterpriseBrain from "@/pages/EnterpriseBrain";
import AIGovernance from "@/pages/AIGovernance";
import Settings from "@/pages/Settings";
import PowerPlatformGovernance from "@/pages/PowerPlatformGovernance";
import WorkshopDetail from "@/pages/WorkshopDetail";
import PPActions from "@/pages/PPActions";
import PPDecisions from "@/pages/PPDecisions";

// Layout
import SidebarLayout from "@/layout/SidebarLayout";

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios defaults
axios.defaults.baseURL = API;

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("bizdesk365_token"));
  const [loading, setLoading] = useState(true);
  const [modules, setModules] = useState([]);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get("/me");
      setUser(response.data);
      await fetchModules();
    } catch (error) {
      console.error("Failed to fetch user:", error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    try {
      const response = await axios.get("/modules");
      setModules(response.data);
    } catch (error) {
      console.error("Failed to fetch modules:", error);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post("/auth/login", { email, password });
      const { access_token } = response.data;
      localStorage.setItem("bizdesk365_token", access_token);
      setToken(access_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || "Erreur de connexion" 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem("bizdesk365_token");
    setToken(null);
    setUser(null);
    setModules([]);
    delete axios.defaults.headers.common["Authorization"];
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, modules, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboards" replace /> : <LoginPage />} />
      
      <Route path="/" element={<ProtectedRoute><SidebarLayout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/dashboards" replace />} />
        <Route path="dashboards" element={<DashboardHome />} />
        <Route path="dashboards/compliance" element={<ComplianceOverview />} />
        <Route path="dashboards/enterprise-brain" element={<EnterpriseBrain />} />
        <Route path="dashboards/ai-governance" element={<AIGovernance />} />
        <Route path="dashboards/power-platform" element={<PowerPlatformGovernance />} />
        <Route path="dashboards/power-platform/workshops/:workshopNumber" element={<WorkshopDetail />} />
        <Route path="dashboards/power-platform/actions" element={<PPActions />} />
        <Route path="dashboards/power-platform/decisions" element={<PPDecisions />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/dashboards" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
