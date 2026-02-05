import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  ShieldCheck, 
  Brain, 
  Bot, 
  FileText, 
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  ArrowRight
} from "lucide-react";
import { Link } from "react-router-dom";

export default function DashboardHome() {
  const [loading, setLoading] = useState(true);
  const [maturity, setMaturity] = useState(null);
  const [quality, setQuality] = useState(null);
  const [aiSummary, setAiSummary] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [maturityRes, qualityRes, aiRes] = await Promise.all([
        axios.get("/compliance/maturity"),
        axios.get("/enterprise-brain/quality"),
        axios.get("/governance/ai/summary")
      ]);
      setMaturity(maturityRes.data);
      setQuality(qualityRes.data);
      setAiSummary(aiRes.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getBandColor = (band) => {
    if (band === "green") return "bg-emerald-500";
    if (band === "yellow") return "bg-amber-500";
    if (band === "red") return "bg-red-500";
    return "bg-slate-400";
  };

  const getBandLabel = (band) => {
    if (band === "green") return "Conforme";
    if (band === "yellow") return "À améliorer";
    if (band === "red") return "Critique";
    return "Non évalué";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const maturityScore = maturity ? Math.round(maturity.score * 100) : 0;
  const maturityBand = maturity ? maturity.band : "gray";
  const isoCount = maturity && maturity.iso_referentials ? maturity.iso_referentials.length : 0;
  
  const iqiScore = quality ? Math.round(quality.iqi_global * 100) : 0;
  const docCount = quality && quality.evidences ? quality.evidences.total_documents : 0;
  const validatedCount = quality && quality.evidences ? quality.evidences.validated_count : 0;
  const freshnessScore = quality && quality.evidences ? quality.evidences.freshness_score : 0;
  
  const authorizedPct = aiSummary ? aiSummary.authorized_percentage : 0;
  const totalUsages = aiSummary ? aiSummary.total_usages : 0;
  const anomalies = aiSummary && aiSummary.traceability ? aiSummary.traceability.anomalies : 0;
  const criticalActions = aiSummary && aiSummary.critical_actions ? aiSummary.critical_actions : [];

  return (
    <div className="space-y-6" data-testid="dashboard-home">
      {/* Page header */}
      <div className="animate-fade-in">
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Tableau de bord
        </h1>
        <p className="text-slate-500 mt-1">
          Vue d'ensemble de votre gouvernance et conformité
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Compliance Maturity Card */}
        <Link to="/dashboards/compliance" className="block">
          <Card className="border border-slate-200 shadow-sm card-hover animate-slide-in-up stagger-1 h-full">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-blue-600" />
                </div>
                <Badge variant="outline" className={`${getBandColor(maturityBand)} text-white border-0`}>
                  {getBandLabel(maturityBand)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm font-medium text-slate-500">Score de Maturité</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {maturityScore}%
                  </span>
                  <span className="text-sm text-slate-400">
                    {isoCount} référentiels ISO
                  </span>
                </div>
                <div className="flex items-center gap-1 text-sm text-blue-600 mt-2">
                  <span>Voir détails</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>

        {/* Enterprise Brain IQI Card */}
        <Link to="/dashboards/enterprise-brain" className="block">
          <Card className="border border-slate-200 shadow-sm card-hover animate-slide-in-up stagger-2 h-full">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-purple-600" />
                </div>
                <Badge variant="outline" className="bg-purple-100 text-purple-700 border-0">
                  Enterprise Brain
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm font-medium text-slate-500">Indice de Qualité (IQI)</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {iqiScore}%
                  </span>
                  <span className="text-sm text-slate-400">
                    {docCount} documents
                  </span>
                </div>
                <div className="flex items-center gap-1 text-sm text-purple-600 mt-2">
                  <span>Voir détails</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>

        {/* AI Governance Card */}
        <Link to="/dashboards/ai-governance" className="block">
          <Card className="border border-slate-200 shadow-sm card-hover animate-slide-in-up stagger-3 h-full">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-emerald-600" />
                </div>
                <Badge variant="outline" className="bg-emerald-100 text-emerald-700 border-0">
                  Gouvernance IA
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm font-medium text-slate-500">IA Autorisée</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {authorizedPct}%
                  </span>
                  <span className="text-sm text-slate-400">
                    {totalUsages} usages
                  </span>
                </div>
                <div className="flex items-center gap-1 text-sm text-emerald-600 mt-2">
                  <span>Voir détails</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Secondary metrics row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-4">
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{validatedCount}</p>
                <p className="text-xs text-slate-500">Documents validés</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-5">
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                <FileText className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{docCount}</p>
                <p className="text-xs text-slate-500">Documents totaux</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-4">
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{anomalies}</p>
                <p className="text-xs text-slate-500">Anomalies IA</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-5">
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                <TrendingUp className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{freshnessScore}%</p>
                <p className="text-xs text-slate-500">Fraîcheur docs</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Critical Actions */}
      {criticalActions.length > 0 && (
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
          <CardHeader>
            <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Actions critiques
            </CardTitle>
            <CardDescription>
              Actions prioritaires à traiter
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {criticalActions.map((action) => {
                const priorityColor = action.priority === "high" ? "bg-red-500" : 
                                      action.priority === "medium" ? "bg-amber-500" : "bg-blue-500";
                const statusStyle = action.status === "pending" ? "bg-red-50 text-red-700 border-red-200" :
                                    action.status === "in_progress" ? "bg-amber-50 text-amber-700 border-amber-200" :
                                    "bg-blue-50 text-blue-700 border-blue-200";
                const statusLabel = action.status === "pending" ? "En attente" :
                                    action.status === "in_progress" ? "En cours" : "Planifié";
                return (
                  <div 
                    key={action.id}
                    className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${priorityColor}`}></div>
                      <span className="text-sm text-slate-700">{action.title}</span>
                    </div>
                    <Badge variant="outline" className={`text-xs ${statusStyle}`}>
                      {statusLabel}
                    </Badge>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
