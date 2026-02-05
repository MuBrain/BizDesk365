import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Bot, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Activity, 
  FileSearch,
  Shield,
  TrendingUp
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

export default function AIGovernance() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get("/governance/ai/summary");
      setSummary(response.data);
    } catch (error) {
      console.error("Error fetching AI governance data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  const pieData = [
    { name: "Autorisée", value: summary?.authorized_percentage || 0, color: "#10b981" },
    { name: "Assistée", value: summary?.assisted_percentage || 0, color: "#f59e0b" },
    { name: "Interdite", value: summary?.forbidden_percentage || 0, color: "#ef4444" },
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "high": return "bg-red-500";
      case "medium": return "bg-amber-500";
      case "low": return "bg-blue-500";
      default: return "bg-slate-400";
    }
  };

  const getStatusStyle = (status) => {
    switch (status) {
      case "pending": return "bg-red-50 text-red-700 border-red-200";
      case "in_progress": return "bg-amber-50 text-amber-700 border-amber-200";
      case "planned": return "bg-blue-50 text-blue-700 border-blue-200";
      default: return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "pending": return "En attente";
      case "in_progress": return "En cours";
      case "planned": return "Planifié";
      default: return status;
    }
  };

  return (
    <div className="space-y-6" data-testid="ai-governance">
      {/* Page header */}
      <div className="animate-fade-in">
        <div className="flex items-center gap-3 mb-1">
          <Bot className="w-8 h-8 text-emerald-600" />
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Gouvernance IA
          </h1>
        </div>
        <p className="text-slate-500">
          Tableau de bord exécutif de l'utilisation de l'IA
        </p>
      </div>

      {/* Main KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-1 border-l-4 border-l-emerald-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 mb-1">IA Autorisée</p>
                <p className="text-3xl font-bold text-emerald-600" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  {summary?.authorized_percentage || 0}%
                </p>
              </div>
              <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Documents validés avec IQI suffisant
            </p>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-2 border-l-4 border-l-amber-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 mb-1">IA Assistée</p>
                <p className="text-3xl font-bold text-amber-600" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  {summary?.assisted_percentage || 0}%
                </p>
              </div>
              <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Supervision humaine requise
            </p>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-3 border-l-4 border-l-red-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 mb-1">IA Interdite</p>
                <p className="text-3xl font-bold text-red-600" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  {summary?.forbidden_percentage || 0}%
                </p>
              </div>
              <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              IQI insuffisant - utilisation bloquée
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Details Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
          <CardHeader>
            <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Répartition des usages IA
            </CardTitle>
            <CardDescription>
              Distribution des {summary?.total_usages || 0} usages enregistrés
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                    labelLine={false}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => `${value}%`}
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Traceability */}
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
          <CardHeader>
            <div className="flex items-center gap-2">
              <FileSearch className="w-5 h-5 text-slate-600" />
              <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Traçabilité
              </CardTitle>
            </div>
            <CardDescription>
              Suivi des usages et audits IA
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-600" />
                  <span className="text-sm text-slate-600">Usages journalisés</span>
                </div>
                <span className="text-xl font-bold text-slate-900">
                  {summary?.traceability?.logged || 0}
                </span>
              </div>
              <Progress value={100} className="h-2" />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-purple-600" />
                  <span className="text-sm text-slate-600">Usages audités</span>
                </div>
                <span className="text-xl font-bold text-slate-900">
                  {summary?.traceability?.audited || 0}
                </span>
              </div>
              <Progress 
                value={summary?.traceability?.logged 
                  ? (summary.traceability.audited / summary.traceability.logged) * 100 
                  : 0
                } 
                className="h-2" 
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span className="text-sm text-slate-600">Anomalies détectées</span>
                </div>
                <span className="text-xl font-bold text-red-600">
                  {summary?.traceability?.anomalies || 0}
                </span>
              </div>
              <Progress 
                value={summary?.traceability?.logged 
                  ? (summary.traceability.anomalies / summary.traceability.logged) * 100 
                  : 0
                } 
                className="h-2 [&>div]:bg-red-500" 
              />
            </div>

            <div className="pt-4 p-4 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-2 text-sm">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                <span className="text-slate-600">Taux de conformité effectif:</span>
                <span className="font-bold text-emerald-600">
                  {summary?.traceability?.logged 
                    ? Math.round(((summary.traceability.logged - summary.traceability.anomalies) / summary.traceability.logged) * 100)
                    : 0}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Critical Actions */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Actions critiques
          </CardTitle>
          <CardDescription>
            Actions prioritaires pour améliorer la gouvernance IA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {summary?.critical_actions?.map((action, index) => (
              <div 
                key={action.id}
                className={`flex items-center justify-between p-4 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors animate-slide-in-up stagger-${Math.min(index + 1, 5)}`}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-3 h-3 rounded-full ${getPriorityColor(action.priority)}`}></div>
                  <div>
                    <p className="font-medium text-slate-900">{action.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Priorité: {action.priority === "high" ? "Haute" : action.priority === "medium" ? "Moyenne" : "Basse"}
                    </p>
                  </div>
                </div>
                <Badge variant="outline" className={getStatusStyle(action.status)}>
                  {getStatusLabel(action.status)}
                </Badge>
              </div>
            ))}

            {(!summary?.critical_actions || summary.critical_actions.length === 0) && (
              <div className="text-center py-8 text-slate-500">
                Aucune action critique en cours
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
