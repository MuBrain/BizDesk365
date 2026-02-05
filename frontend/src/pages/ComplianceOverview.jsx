import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ShieldCheck, TrendingUp, Calendar, CheckCircle2, AlertCircle, FileText } from "lucide-react";

export default function ComplianceOverview() {
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState([]);
  const [maturity, setMaturity] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [kpisRes, maturityRes] = await Promise.all([
        axios.get("/compliance/kpis/latest"),
        axios.get("/compliance/maturity")
      ]);
      setKpis(kpisRes.data);
      setMaturity(maturityRes.data);
    } catch (error) {
      console.error("Error fetching compliance data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getBandColor = (band) => {
    switch (band) {
      case "green": return { bg: "bg-emerald-500", text: "text-emerald-700", light: "bg-emerald-50" };
      case "yellow": return { bg: "bg-amber-500", text: "text-amber-700", light: "bg-amber-50" };
      case "red": return { bg: "bg-red-500", text: "text-red-700", light: "bg-red-50" };
      default: return { bg: "bg-slate-400", text: "text-slate-700", light: "bg-slate-50" };
    }
  };

  const getBandLabel = (band) => {
    switch (band) {
      case "green": return "Conforme";
      case "yellow": return "À améliorer";
      case "red": return "Critique";
      default: return "Non évalué";
    }
  };

  const getKPIIcon = (name) => {
    switch (name) {
      case "MaturityIndex": return TrendingUp;
      case "PolicyCoverage": return FileText;
      case "AuditFreshnessDays": return Calendar;
      default: return CheckCircle2;
    }
  };

  const getKPILabel = (name) => {
    switch (name) {
      case "MaturityIndex": return "Indice de Maturité";
      case "PolicyCoverage": return "Couverture des Politiques";
      case "AuditFreshnessDays": return "Fraîcheur des Audits";
      default: return name;
    }
  };

  const formatKPIValue = (kpi) => {
    if (kpi.name === "AuditFreshnessDays") {
      return `${kpi.value} jours`;
    }
    return `${Math.round(kpi.value * 100)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const bandColors = getBandColor(maturity?.band);

  return (
    <div className="space-y-6" data-testid="compliance-overview">
      {/* Page header */}
      <div className="animate-fade-in">
        <div className="flex items-center gap-3 mb-1">
          <ShieldCheck className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Conformité ISO
          </h1>
        </div>
        <p className="text-slate-500">
          Suivi de la conformité et du score de maturité
        </p>
      </div>

      {/* Maturity Score Card */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Score de Maturité Global
              </CardTitle>
              <CardDescription>
                Basé sur les référentiels: {maturity?.iso_referentials?.join(", ") || "Aucun"}
              </CardDescription>
            </div>
            <Badge className={`${bandColors.bg} text-white border-0`}>
              {getBandLabel(maturity?.band)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Score display */}
            <div className="flex items-center gap-8">
              <div className="relative">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#e2e8f0"
                    strokeWidth="12"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke={maturity?.band === "green" ? "#10b981" : maturity?.band === "yellow" ? "#f59e0b" : "#ef4444"}
                    strokeWidth="12"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${(maturity?.score || 0) * 351.86} 351.86`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {Math.round((maturity?.score || 0) * 100)}%
                  </span>
                </div>
              </div>

              <div className="flex-1 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(maturity?.inputs || {}).map(([key, value]) => (
                    <div key={key} className="p-3 bg-slate-50 rounded-lg">
                      <p className="text-xs text-slate-500 mb-1">{getKPILabel(key)}</p>
                      <p className="text-lg font-semibold text-slate-900">
                        {key === "AuditFreshnessDays" ? `${value} jours` : `${Math.round(value * 100)}%`}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Band explanation */}
            <div className={`p-4 rounded-lg ${bandColors.light} border border-slate-200`}>
              <div className="flex items-start gap-3">
                {maturity?.band === "green" ? (
                  <CheckCircle2 className={`w-5 h-5 ${bandColors.text} mt-0.5`} />
                ) : (
                  <AlertCircle className={`w-5 h-5 ${bandColors.text} mt-0.5`} />
                )}
                <div>
                  <p className={`font-medium ${bandColors.text}`}>
                    {maturity?.band === "green" 
                      ? "Niveau de conformité satisfaisant"
                      : maturity?.band === "yellow"
                        ? "Niveau de conformité intermédiaire - des améliorations sont nécessaires"
                        : "Niveau de conformité critique - actions urgentes requises"
                    }
                  </p>
                  <p className="text-sm text-slate-600 mt-1">
                    Score calculé à partir de l'indice de maturité (40%), la couverture des politiques (40%) et la fraîcheur des audits (20%).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {kpis.map((kpi, index) => {
          const Icon = getKPIIcon(kpi.name);
          const isPercentage = kpi.name !== "AuditFreshnessDays";
          const progressValue = isPercentage ? kpi.value * 100 : Math.max(0, 100 - (kpi.value / 30) * 100);
          
          return (
            <Card 
              key={kpi.id} 
              className={`border border-slate-200 shadow-sm animate-slide-in-up stagger-${index + 1}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500 mb-1">{getKPILabel(kpi.name)}</p>
                <p className="text-2xl font-bold text-slate-900 mb-3" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  {formatKPIValue(kpi)}
                </p>
                <Progress 
                  value={progressValue} 
                  className="h-2"
                />
                <p className="text-xs text-slate-400 mt-2">
                  Mesuré le {new Date(kpi.measured_at).toLocaleDateString("fr-FR")}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* ISO Referentials */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Référentiels ISO actifs
          </CardTitle>
          <CardDescription>
            Normes ISO configurées pour votre organisation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            {maturity?.iso_referentials?.map((iso) => (
              <div 
                key={iso}
                className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg border border-blue-100"
              >
                <ShieldCheck className="w-4 h-4 text-blue-600" />
                <span className="font-medium text-blue-700">{iso}</span>
              </div>
            ))}
            {(!maturity?.iso_referentials || maturity.iso_referentials.length === 0) && (
              <p className="text-slate-500">Aucun référentiel ISO configuré</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
