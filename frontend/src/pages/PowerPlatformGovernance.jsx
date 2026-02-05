import { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Zap, 
  CheckCircle2, 
  Clock, 
  AlertTriangle,
  ArrowRight,
  Users,
  FileText,
  Target,
  TrendingUp,
  Calendar,
  ListTodo,
  FileCheck,
  Play,
  Pause
} from "lucide-react";

export default function PowerPlatformGovernance() {
  const [loading, setLoading] = useState(true);
  const [program, setProgram] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [workshops, setWorkshops] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [programRes, kpisRes, workshopsRes] = await Promise.all([
        axios.get("/power-platform/program"),
        axios.get("/power-platform/kpis"),
        axios.get("/power-platform/workshops")
      ]);
      setProgram(programRes.data);
      setKpis(kpisRes.data);
      setWorkshops(workshopsRes.data);
    } catch (error) {
      console.error("Error fetching Power Platform data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    if (status === "completed") return "bg-emerald-500";
    if (status === "in_progress") return "bg-blue-500";
    return "bg-slate-300";
  };

  const getStatusBadge = (status) => {
    if (status === "completed") return { label: "Terminé", className: "bg-emerald-100 text-emerald-700" };
    if (status === "in_progress") return { label: "En cours", className: "bg-blue-100 text-blue-700" };
    return { label: "Non démarré", className: "bg-slate-100 text-slate-600" };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  const completionPct = kpis ? kpis.workshop_completion_pct : 0;
  const itemsProgress = kpis ? Math.round((kpis.items_done + kpis.items_validated) / kpis.items_total * 100) : 0;

  return (
    <div className="space-y-6" data-testid="power-platform-page">
      {/* Page header */}
      <div className="animate-fade-in">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 mb-1">
            <Zap className="w-8 h-8 text-amber-500" />
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Gouvernance Power Platform
              </h1>
              <p className="text-slate-500">
                Programme en 10 ateliers
              </p>
            </div>
          </div>
          <Badge className={completionPct >= 100 ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}>
            {completionPct}% complété
          </Badge>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-1">
          <CardContent className="pt-4">
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                {kpis ? kpis.workshops_completed : 0}/10
              </span>
              <span className="text-xs text-slate-500">Ateliers terminés</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-2">
          <CardContent className="pt-4">
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                {itemsProgress}%
              </span>
              <span className="text-xs text-slate-500">Items complétés</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-3">
          <CardContent className="pt-4">
            <div className="flex flex-col">
              <span className={`text-2xl font-bold ${kpis && kpis.actions_open_count > 10 ? "text-amber-600" : "text-slate-900"}`} style={{ fontFamily: 'Manrope, sans-serif' }}>
                {kpis ? kpis.actions_open_count : 0}
              </span>
              <span className="text-xs text-slate-500">Actions ouvertes</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-4">
          <CardContent className="pt-4">
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                {kpis ? kpis.actions_ageing_avg_days : 0}j
              </span>
              <span className="text-xs text-slate-500">Âge moyen actions</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-5">
          <CardContent className="pt-4">
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                {kpis ? kpis.decisions_count : 0}
              </span>
              <span className="text-xs text-slate-500">Décisions</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-5">
          <CardContent className="pt-4">
            <div className="flex flex-col">
              <span className={`text-2xl font-bold ${kpis && kpis.ownership_missing_pct > 20 ? "text-red-600" : "text-slate-900"}`} style={{ fontFamily: 'Manrope, sans-serif' }}>
                {kpis ? kpis.ownership_missing_pct : 0}%
              </span>
              <span className="text-xs text-slate-500">Sans propriétaire</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline horizontal */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Progression des ateliers
          </CardTitle>
          <CardDescription>
            Avancement dans le programme de gouvernance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="w-full whitespace-nowrap pb-4">
            <div className="flex gap-2 pb-4">
              {workshops.map((ws, index) => {
                const statusBadge = getStatusBadge(ws.status);
                const isActive = ws.status === "in_progress";
                const isCompleted = ws.status === "completed";
                
                return (
                  <div key={ws.workshop_number} className="flex items-center">
                    <Link 
                      to={`/dashboards/power-platform/workshops/${ws.workshop_number}`}
                      className="block"
                    >
                      <div 
                        className={`
                          relative flex-shrink-0 w-48 p-4 rounded-xl border-2 transition-all duration-200
                          ${isCompleted 
                            ? "border-emerald-500 bg-emerald-50 hover:bg-emerald-100" 
                            : isActive 
                              ? "border-blue-500 bg-blue-50 hover:bg-blue-100 ring-2 ring-blue-200" 
                              : "border-slate-200 bg-white hover:bg-slate-50"
                          }
                        `}
                      >
                        {/* Workshop number badge */}
                        <div className={`
                          absolute -top-3 left-4 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                          ${isCompleted 
                            ? "bg-emerald-500 text-white" 
                            : isActive 
                              ? "bg-blue-500 text-white" 
                              : "bg-slate-200 text-slate-600"
                          }
                        `}>
                          {ws.workshop_number}
                        </div>

                        {/* Status icon */}
                        <div className="absolute -top-3 right-4">
                          {isCompleted ? (
                            <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                          ) : isActive ? (
                            <Play className="w-6 h-6 text-blue-500" />
                          ) : (
                            <Pause className="w-6 h-6 text-slate-300" />
                          )}
                        </div>

                        <div className="mt-2">
                          <h4 className="font-semibold text-slate-900 text-sm truncate mb-1" title={ws.title}>
                            {ws.title}
                          </h4>
                          <div className="flex items-center gap-2 mb-2">
                            <Progress 
                              value={ws.items_progress_pct} 
                              className="h-1.5 flex-1"
                            />
                            <span className="text-xs text-slate-500 whitespace-nowrap">
                              {ws.items_done}/{ws.items_total}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-xs text-slate-500">
                            {ws.open_actions_count > 0 && (
                              <span className="flex items-center gap-1">
                                <ListTodo className="w-3 h-3" />
                                {ws.open_actions_count}
                              </span>
                            )}
                            {ws.decisions_count > 0 && (
                              <span className="flex items-center gap-1">
                                <FileCheck className="w-3 h-3" />
                                {ws.decisions_count}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </Link>
                    
                    {/* Connector line */}
                    {index < workshops.length - 1 && (
                      <div className={`w-6 h-1 mx-1 rounded ${
                        isCompleted ? "bg-emerald-400" : "bg-slate-200"
                      }`} />
                    )}
                  </div>
                );
              })}
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Tabs for detailed views */}
      <Tabs defaultValue="workshops" className="space-y-4">
        <TabsList className="bg-slate-100">
          <TabsTrigger value="workshops" className="data-[state=active]:bg-white">
            <Target className="w-4 h-4 mr-2" />
            Ateliers
          </TabsTrigger>
          <TabsTrigger value="actions" className="data-[state=active]:bg-white">
            <ListTodo className="w-4 h-4 mr-2" />
            Actions
          </TabsTrigger>
          <TabsTrigger value="decisions" className="data-[state=active]:bg-white">
            <FileCheck className="w-4 h-4 mr-2" />
            Décisions
          </TabsTrigger>
        </TabsList>

        {/* Workshops Tab */}
        <TabsContent value="workshops" className="space-y-4">
          <div className="grid gap-4">
            {workshops.map((ws) => {
              const statusBadge = getStatusBadge(ws.status);
              return (
                <Link 
                  key={ws.workshop_number}
                  to={`/dashboards/power-platform/workshops/${ws.workshop_number}`}
                >
                  <Card className="border border-slate-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`
                            w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg
                            ${ws.status === "completed" 
                              ? "bg-emerald-100 text-emerald-700" 
                              : ws.status === "in_progress" 
                                ? "bg-blue-100 text-blue-700" 
                                : "bg-slate-100 text-slate-500"
                            }
                          `}>
                            {ws.workshop_number}
                          </div>
                          <div>
                            <h3 className="font-semibold text-slate-900">{ws.title}</h3>
                            <p className="text-sm text-slate-500 line-clamp-1">{ws.description}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-6">
                          <div className="text-center">
                            <p className="text-lg font-bold text-slate-900">{ws.items_progress_pct}%</p>
                            <p className="text-xs text-slate-500">Items</p>
                          </div>
                          <div className="text-center">
                            <p className="text-lg font-bold text-slate-900">{ws.open_actions_count}</p>
                            <p className="text-xs text-slate-500">Actions</p>
                          </div>
                          <div className="text-center">
                            <p className="text-lg font-bold text-slate-900">{ws.decisions_count}</p>
                            <p className="text-xs text-slate-500">Décisions</p>
                          </div>
                          <Badge className={statusBadge.className}>
                            {statusBadge.label}
                          </Badge>
                          <ArrowRight className="w-5 h-5 text-slate-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        </TabsContent>

        {/* Actions Tab - Quick view */}
        <TabsContent value="actions">
          <Card className="border border-slate-200 shadow-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  Actions ouvertes
                </CardTitle>
                <Link to="/dashboards/power-platform/actions">
                  <Button variant="outline" size="sm">
                    Voir tout
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-slate-500">
                <ListTodo className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p className="font-medium">{kpis ? kpis.actions_open_count : 0} actions ouvertes</p>
                <p className="text-sm">Âge moyen: {kpis ? kpis.actions_ageing_avg_days : 0} jours</p>
                <Link to="/dashboards/power-platform/actions">
                  <Button className="mt-4 bg-amber-500 hover:bg-amber-600">
                    Gérer les actions
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Decisions Tab - Quick view */}
        <TabsContent value="decisions">
          <Card className="border border-slate-200 shadow-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  Décisions enregistrées
                </CardTitle>
                <Link to="/dashboards/power-platform/decisions">
                  <Button variant="outline" size="sm">
                    Voir tout
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-slate-500">
                <FileCheck className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p className="font-medium">{kpis ? kpis.decisions_count : 0} décisions</p>
                <p className="text-sm">Preuves enregistrées: {kpis ? kpis.evidence_count : 0}</p>
                <Link to="/dashboards/power-platform/decisions">
                  <Button className="mt-4 bg-amber-500 hover:bg-amber-600">
                    Voir les décisions
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
