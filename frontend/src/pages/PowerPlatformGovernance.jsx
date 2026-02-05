import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Zap, Lock, ArrowRight, BarChart3, Shield, Settings } from "lucide-react";

export default function PowerPlatformGovernance() {
  return (
    <div className="space-y-6" data-testid="power-platform-page">
      {/* Page header */}
      <div className="animate-fade-in">
        <div className="flex items-center gap-3 mb-1">
          <Zap className="w-8 h-8 text-amber-500" />
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Power Platform Governance
          </h1>
          <Badge className="bg-amber-100 text-amber-700 border-0">
            Bientôt disponible
          </Badge>
        </div>
        <p className="text-slate-500">
          Gouvernance Microsoft Power Platform
        </p>
      </div>

      {/* Coming Soon Card */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardContent className="py-12">
          <div className="text-center max-w-lg mx-auto">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-amber-100 flex items-center justify-center">
              <Lock className="w-10 h-10 text-amber-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-3" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Module en cours de développement
            </h2>
            <p className="text-slate-500 mb-6">
              Le module Power Platform Governance sera bientôt disponible. 
              Il vous permettra de surveiller et gouverner vos applications Power Apps, 
              flux Power Automate et bots Power Virtual Agents.
            </p>
            <Button disabled className="bg-slate-300 text-slate-500 cursor-not-allowed">
              <Zap className="w-4 h-4 mr-2" />
              Activer le module
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Feature Preview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-1 opacity-60">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center mb-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
            </div>
            <CardTitle className="text-base" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Analytics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">
              Tableau de bord des usages Power Apps et Power Automate avec métriques détaillées.
            </p>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-2 opacity-60">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center mb-2">
              <Shield className="w-5 h-5 text-blue-600" />
            </div>
            <CardTitle className="text-base" style={{ fontFamily: 'Manrope, sans-serif' }}>
              DLP Policies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">
              Gestion des politiques de prévention des pertes de données pour vos environnements.
            </p>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 shadow-sm animate-slide-in-up stagger-3 opacity-60">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center mb-2">
              <Settings className="w-5 h-5 text-emerald-600" />
            </div>
            <CardTitle className="text-base" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Environnements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">
              Vue centralisée de tous vos environnements Power Platform avec leur état de santé.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Placeholder KPIs */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Aperçu des KPIs (données de démonstration)
          </CardTitle>
          <CardDescription>
            Ces métriques seront disponibles une fois le module activé
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 opacity-60">
              <p className="text-xs text-slate-500 mb-1">Power Apps</p>
              <p className="text-2xl font-bold text-slate-400">--</p>
            </div>
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 opacity-60">
              <p className="text-xs text-slate-500 mb-1">Flux Automate</p>
              <p className="text-2xl font-bold text-slate-400">--</p>
            </div>
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 opacity-60">
              <p className="text-xs text-slate-500 mb-1">Connecteurs</p>
              <p className="text-2xl font-bold text-slate-400">--</p>
            </div>
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 opacity-60">
              <p className="text-xs text-slate-500 mb-1">Environnements</p>
              <p className="text-2xl font-bold text-slate-400">--</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
