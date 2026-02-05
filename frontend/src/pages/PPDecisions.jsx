import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Toaster, toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  ArrowLeft, 
  Plus,
  FileCheck,
  Calendar,
  User,
  Loader2,
  Trash2,
  ExternalLink
} from "lucide-react";

export default function PPDecisions() {
  const [loading, setLoading] = useState(true);
  const [decisions, setDecisions] = useState([]);
  const [workshops, setWorkshops] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newDecisionText, setNewDecisionText] = useState("");
  const [newDecisionWorkshop, setNewDecisionWorkshop] = useState("null");
  const [newDecisionLinks, setNewDecisionLinks] = useState("");
  const [saving, setSaving] = useState(false);
  const [filterWorkshop, setFilterWorkshop] = useState("all");

  useEffect(function() {
    fetchData();
  }, []);

  const fetchData = async function() {
    try {
      const decisionsRes = await axios.get("/power-platform/decisions");
      const workshopsRes = await axios.get("/power-platform/workshops");
      setDecisions(decisionsRes.data);
      setWorkshops(workshopsRes.data);
    } catch (error) {
      console.error("Error fetching decisions:", error);
      toast.error("Erreur lors du chargement");
    } finally {
      setLoading(false);
    }
  };

  const openCreateDialog = function() {
    setNewDecisionText("");
    setNewDecisionWorkshop("null");
    setNewDecisionLinks("");
    setDialogOpen(true);
  };

  const handleSave = async function() {
    if (!newDecisionText) {
      toast.error("Le texte de la décision est requis");
      return;
    }
    
    setSaving(true);
    try {
      const wsNum = newDecisionWorkshop === "null" ? null : parseInt(newDecisionWorkshop);
      const links = newDecisionLinks.split("\n").filter(function(l) { return l.trim(); });
      
      await axios.post("/power-platform/decisions", {
        decision_text: newDecisionText,
        workshop_number: wsNum,
        evidence_links: links
      });
      toast.success("Décision enregistrée");
      setDialogOpen(false);
      fetchData();
    } catch (error) {
      toast.error("Erreur lors de l'enregistrement");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async function(decisionId) {
    if (!confirm("Supprimer cette décision ?")) return;
    
    try {
      await axios.delete("/power-platform/decisions/" + decisionId);
      toast.success("Décision supprimée");
      fetchData();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const filteredDecisions = decisions.filter(function(d) {
    if (filterWorkshop === "all") return true;
    if (filterWorkshop === "none") return !d.workshop_number;
    return d.workshop_number === parseInt(filterWorkshop);
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="pp-decisions-page">
      <Toaster position="top-right" richColors />

      {/* Header */}
      <div className="animate-fade-in">
        <Link to="/dashboards/power-platform" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Retour au programme
        </Link>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileCheck className="w-8 h-8 text-amber-500" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Journal des décisions
              </h1>
              <p className="text-slate-500">
                {decisions.length} décisions enregistrées
              </p>
            </div>
          </div>
          <Button onClick={openCreateDialog} className="bg-amber-500 hover:bg-amber-600">
            <Plus className="w-4 h-4 mr-2" />
            Nouvelle décision
          </Button>
        </div>
      </div>

      {/* Filter */}
      <Card className="border border-slate-200 shadow-sm">
        <CardContent className="py-4">
          <div className="flex items-center gap-2">
            <Label className="text-sm text-slate-500">Atelier:</Label>
            <Select value={filterWorkshop} onValueChange={setFilterWorkshop}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous</SelectItem>
                <SelectItem value="none">Non lié</SelectItem>
                {workshops.map(function(ws) {
                  return (
                    <SelectItem key={ws.workshop_number} value={ws.workshop_number.toString()}>
                      Atelier {ws.workshop_number}
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Decisions List */}
      <div className="space-y-4">
        {filteredDecisions.length === 0 ? (
          <Card className="border border-slate-200 shadow-sm">
            <CardContent className="py-12 text-center">
              <FileCheck className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p className="text-slate-500">Aucune décision enregistrée</p>
              <Button onClick={openCreateDialog} className="mt-4 bg-amber-500 hover:bg-amber-600">
                <Plus className="w-4 h-4 mr-2" />
                Créer une décision
              </Button>
            </CardContent>
          </Card>
        ) : (
          filteredDecisions.map(function(decision) {
            const evidenceLinks = decision.evidence_links || [];
            return (
              <Card key={decision.id} className="border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {decision.workshop_number && (
                          <Badge variant="outline">Atelier {decision.workshop_number}</Badge>
                        )}
                        <span className="text-sm text-slate-500 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(decision.decided_at).toLocaleDateString("fr-FR")}
                        </span>
                        <span className="text-sm text-slate-500 flex items-center gap-1">
                          <User className="w-3 h-3" />
                          {decision.decided_by}
                        </span>
                      </div>
                      <p className="text-slate-900 whitespace-pre-wrap">{decision.decision_text}</p>
                      
                      {evidenceLinks.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {evidenceLinks.map(function(link, index) {
                            return (
                              <a 
                                key={index}
                                href={link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                              >
                                <ExternalLink className="w-3 h-3" />
                                Preuve {index + 1}
                              </a>
                            );
                          })}
                        </div>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={function() { handleDelete(decision.id); }}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nouvelle décision</DialogTitle>
            <DialogDescription>
              Enregistrez une décision prise lors du programme de gouvernance
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Décision *</Label>
              <Textarea
                value={newDecisionText}
                onChange={function(e) { setNewDecisionText(e.target.value); }}
                placeholder="Décrivez la décision prise..."
                rows={4}
              />
            </div>
            
            <div className="space-y-2">
              <Label>Atelier lié</Label>
              <Select value={newDecisionWorkshop} onValueChange={setNewDecisionWorkshop}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="null">Aucun</SelectItem>
                  {workshops.map(function(ws) {
                    return (
                      <SelectItem key={ws.workshop_number} value={ws.workshop_number.toString()}>
                        Atelier {ws.workshop_number}: {ws.title}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Liens vers les preuves (optionnel)</Label>
              <Input
                value={newDecisionLinks}
                onChange={function(e) { setNewDecisionLinks(e.target.value); }}
                placeholder="Un lien par ligne"
              />
              <p className="text-xs text-slate-500">Ajoutez des URLs vers les documents de preuve</p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={function() { setDialogOpen(false); }}>
              Annuler
            </Button>
            <Button onClick={handleSave} disabled={saving} className="bg-amber-500 hover:bg-amber-600">
              {saving ? (
                <span className="flex items-center">
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Enregistrement...
                </span>
              ) : (
                "Enregistrer"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
