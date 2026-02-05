import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Brain, FileText, CheckCircle2, AlertTriangle, Clock, ExternalLink, Bot } from "lucide-react";

export default function EnterpriseBrain() {
  const [loading, setLoading] = useState(true);
  const [quality, setQuality] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [aiUsage, setAiUsage] = useState({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [qualityRes, docsRes] = await Promise.all([
        axios.get("/enterprise-brain/quality"),
        axios.get("/enterprise-brain/documents")
      ]);
      setQuality(qualityRes.data);
      setDocuments(docsRes.data);
      
      // Fetch AI usage for each document
      const usagePromises = docsRes.data.map(doc => 
        axios.get(`/ai/usage/document/${doc.id}`).catch(() => null)
      );
      const usageResults = await Promise.all(usagePromises);
      const usageMap = {};
      usageResults.forEach((res, index) => {
        if (res) {
          usageMap[docsRes.data[index].id] = res.data;
        }
      });
      setAiUsage(usageMap);
    } catch (error) {
      console.error("Error fetching enterprise brain data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "authorized":
        return <Badge className="badge-authorized">IA Autorisée</Badge>;
      case "assisted":
        return <Badge className="badge-assisted">IA Assistée</Badge>;
      case "forbidden":
        return <Badge className="badge-forbidden">IA Interdite</Badge>;
      default:
        return <Badge variant="outline">Non évalué</Badge>;
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return "text-emerald-600";
    if (score >= 0.6) return "text-amber-600";
    return "text-red-600";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="enterprise-brain">
      {/* Page header */}
      <div className="animate-fade-in">
        <div className="flex items-center gap-3 mb-1">
          <Brain className="w-8 h-8 text-purple-600" />
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Enterprise Brain
          </h1>
        </div>
        <p className="text-slate-500">
          Qualité de l'information et gestion documentaire
        </p>
      </div>

      {/* IQI Score Card */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Indice de Qualité de l'Information (IQI)
              </CardTitle>
              <CardDescription>
                Score global basé sur la validation, la confiance et la fraîcheur des documents
              </CardDescription>
            </div>
            <Badge className="bg-purple-100 text-purple-700 border-0">
              {quality?.evidences?.total_documents || 0} documents
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* IQI Gauge */}
            <div className="flex items-center justify-center">
              <div className="relative">
                <svg className="w-40 h-40 transform -rotate-90">
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    stroke="#e2e8f0"
                    strokeWidth="14"
                    fill="none"
                  />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    stroke="#8b5cf6"
                    strokeWidth="14"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${(quality?.iqi_global || 0) * 439.82} 439.82`}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {Math.round((quality?.iqi_global || 0) * 100)}%
                  </span>
                  <span className="text-sm text-slate-500">IQI Global</span>
                </div>
              </div>
            </div>

            {/* Breakdown */}
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Taux de validation</span>
                  <span className="font-medium">{quality?.evidences?.validation_rate || 0}%</span>
                </div>
                <Progress value={quality?.evidences?.validation_rate || 0} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Confiance moyenne</span>
                  <span className="font-medium">{quality?.evidences?.avg_confidence || 0}%</span>
                </div>
                <Progress value={quality?.evidences?.avg_confidence || 0} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Fraîcheur</span>
                  <span className="font-medium">{quality?.evidences?.freshness_score || 0}%</span>
                </div>
                <Progress value={quality?.evidences?.freshness_score || 0} className="h-2" />
              </div>

              <div className="pt-2 grid grid-cols-2 gap-4">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-500">Documents validés</p>
                  <p className="text-xl font-bold text-slate-900">{quality?.evidences?.validated_count || 0}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-500">Documents frais</p>
                  <p className="text-xl font-bold text-slate-900">{quality?.evidences?.fresh_documents || 0}</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Documents
          </CardTitle>
          <CardDescription>
            Liste des documents avec leur statut d'utilisation IA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50">
                  <TableHead className="font-semibold text-slate-600">Document</TableHead>
                  <TableHead className="font-semibold text-slate-600">Type</TableHead>
                  <TableHead className="font-semibold text-slate-600">Propriétaire</TableHead>
                  <TableHead className="font-semibold text-slate-600 text-center">Confiance</TableHead>
                  <TableHead className="font-semibold text-slate-600 text-center">Validé</TableHead>
                  <TableHead className="font-semibold text-slate-600 text-center">Usage IA</TableHead>
                  <TableHead className="font-semibold text-slate-600">Mis à jour</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc, index) => (
                  <TableRow 
                    key={doc.id}
                    className={`animate-slide-in-up stagger-${Math.min(index + 1, 5)} hover:bg-slate-50 transition-colors`}
                  >
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-slate-400" />
                        <span className="font-medium text-slate-900">{doc.title}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="bg-slate-50">
                        {doc.doc_type}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-slate-600">{doc.owner}</TableCell>
                    <TableCell className="text-center">
                      <span className={`font-semibold ${getConfidenceColor(doc.confidence_score)}`}>
                        {Math.round(doc.confidence_score * 100)}%
                      </span>
                    </TableCell>
                    <TableCell className="text-center">
                      {doc.validated ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-amber-500 mx-auto" />
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      {aiUsage[doc.id] ? (
                        getStatusBadge(aiUsage[doc.id].usage_status)
                      ) : (
                        <Badge variant="outline">-</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-slate-500 text-sm">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(doc.last_updated).toLocaleDateString("fr-FR")}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* AI Usage Legend */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-slate-600" />
            <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Légende des usages IA
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100">
              <div className="flex items-center gap-2 mb-2">
                <Badge className="badge-authorized">IA Autorisée</Badge>
              </div>
              <p className="text-sm text-slate-600">
                Document validé avec un score IQI ≥ 80%. Utilisation sans restriction.
              </p>
            </div>
            <div className="p-4 bg-amber-50 rounded-lg border border-amber-100">
              <div className="flex items-center gap-2 mb-2">
                <Badge className="badge-assisted">IA Assistée</Badge>
              </div>
              <p className="text-sm text-slate-600">
                Score IQI entre 60% et 80%. Utilisation avec supervision humaine requise.
              </p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg border border-red-100">
              <div className="flex items-center gap-2 mb-2">
                <Badge className="badge-forbidden">IA Interdite</Badge>
              </div>
              <p className="text-sm text-slate-600">
                Score IQI {"<"} 60% ou document non validé. Utilisation interdite.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
