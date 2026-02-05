import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Toaster, toast } from "sonner";
import {
  Dialog,
  DialogContent,
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
  CheckCircle2, 
  Play,
  User,
  Calendar,
  FileText,
  ChevronRight,
  Loader2,
  CheckCheck,
  Save
} from "lucide-react";

export default function WorkshopDetail() {
  const { workshopNumber } = useParams();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [workshop, setWorkshop] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [itemDialogOpen, setItemDialogOpen] = useState(false);

  useEffect(() => {
    fetchWorkshop();
  }, [workshopNumber]);

  const fetchWorkshop = async () => {
    try {
      const response = await axios.get("/power-platform/workshops/" + workshopNumber);
      setWorkshop(response.data);
    } catch (error) {
      console.error("Error fetching workshop:", error);
      toast.error("Erreur lors du chargement de l'atelier");
    } finally {
      setLoading(false);
    }
  };

  const handleStartWorkshop = async () => {
    try {
      await axios.patch("/power-platform/workshops/" + workshopNumber, {
        status: "in_progress"
      });
      toast.success("Atelier démarré");
      fetchWorkshop();
    } catch (error) {
      toast.error("Erreur lors du démarrage");
    }
  };

  const handleCriteriaChange = async (criterion, checked) => {
    if (!workshop || !workshop.completion_criteria_state) return;
    const newState = {};
    Object.keys(workshop.completion_criteria_state).forEach(key => {
      newState[key] = workshop.completion_criteria_state[key];
    });
    newState[criterion] = checked;
    
    try {
      await axios.patch("/power-platform/workshops/" + workshopNumber, {
        completion_criteria_state: newState
      });
      setWorkshop(function(prev) {
        return { ...prev, completion_criteria_state: newState };
      });
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const openItemDialog = (item) => {
    const itemCopy = JSON.parse(JSON.stringify(item));
    setSelectedItem(itemCopy);
    setItemDialogOpen(true);
  };

  const handleItemUpdate = async () => {
    if (!selectedItem) return;
    
    setSaving(true);
    try {
      await axios.patch("/power-platform/items/" + selectedItem.item_id, {
        status: selectedItem.status,
        owner_user_id: selectedItem.owner_user_id || null,
        due_date: selectedItem.due_date || null,
        notes_markdown: selectedItem.notes_markdown || null,
        acceptance_state: selectedItem.acceptance_state
      });
      toast.success("Item mis à jour");
      setItemDialogOpen(false);
      fetchWorkshop();
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    } finally {
      setSaving(false);
    }
  };

  const handleValidateItem = async (itemId, validated) => {
    try {
      await axios.post("/power-platform/items/" + itemId + "/validate", {
        validated: validated
      });
      toast.success(validated ? "Item validé" : "Validation retirée");
      fetchWorkshop();
    } catch (error) {
      toast.error("Erreur lors de la validation");
    }
  };

  const handleAcceptanceCriteriaChange = (criterion, checked) => {
    if (!selectedItem) return;
    const newState = {};
    if (selectedItem.acceptance_state) {
      Object.keys(selectedItem.acceptance_state).forEach(key => {
        newState[key] = selectedItem.acceptance_state[key];
      });
    }
    newState[criterion] = checked;
    setSelectedItem(function(prev) {
      return { ...prev, acceptance_state: newState };
    });
  };

  const getStatusBadge = (status) => {
    if (status === "validated") return { label: "Validé", className: "bg-emerald-100 text-emerald-700" };
    if (status === "done") return { label: "Terminé", className: "bg-blue-100 text-blue-700" };
    if (status === "in_progress") return { label: "En cours", className: "bg-amber-100 text-amber-700" };
    return { label: "Non démarré", className: "bg-slate-100 text-slate-600" };
  };

  const getRequirementBadge = (req) => {
    if (req === "OBLIGATOIRE") return "bg-red-100 text-red-700";
    if (req === "OPTIONNEL") return "bg-slate-100 text-slate-600";
    return "bg-amber-100 text-amber-700";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  if (!workshop) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">Atelier non trouvé</p>
        <Link to="/dashboards/power-platform">
          <Button className="mt-4">Retour</Button>
        </Link>
      </div>
    );
  }

  const completionCriteria = workshop.completion_criteria || [];
  const completionState = workshop.completion_criteria_state || {};
  const items = workshop.items || [];
  
  let completedCriteriaCount = 0;
  completionCriteria.forEach(function(c) {
    if (completionState[c]) completedCriteriaCount++;
  });
  
  let itemsCompletedCount = 0;
  items.forEach(function(item) {
    if (item.status === "done" || item.status === "validated") {
      itemsCompletedCount++;
    }
  });

  return (
    <div className="space-y-6" data-testid="workshop-detail">
      <Toaster position="top-right" richColors />

      {/* Header */}
      <div className="animate-fade-in">
        <Link to="/dashboards/power-platform" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Retour au programme
        </Link>
        
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className={`
              w-16 h-16 rounded-xl flex items-center justify-center font-bold text-2xl
              ${workshop.status === "completed" 
                ? "bg-emerald-100 text-emerald-700" 
                : workshop.status === "in_progress" 
                  ? "bg-blue-100 text-blue-700" 
                  : "bg-slate-100 text-slate-500"
              }
            `}>
              {workshop.workshop_number}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Atelier {workshop.workshop_number}: {workshop.title}
              </h1>
              <p className="text-slate-500 mt-1">{workshop.description}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {workshop.status === "not_started" && (
              <Button onClick={handleStartWorkshop} className="bg-blue-600 hover:bg-blue-700">
                <Play className="w-4 h-4 mr-2" />
                Démarrer l'atelier
              </Button>
            )}
            <Badge className={getStatusBadge(workshop.status).className}>
              {getStatusBadge(workshop.status).label}
            </Badge>
          </div>
        </div>
      </div>

      {/* Progress Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Completion Criteria */}
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
              <CheckCheck className="w-5 h-5 text-emerald-600" />
              Critères de complétion
            </CardTitle>
            <CardDescription>
              {completedCriteriaCount}/{completionCriteria.length} critères validés
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={(completedCriteriaCount / completionCriteria.length) * 100} className="h-2 mb-4" />
            <div className="space-y-3">
              {completionCriteria.map(function(criterion, index) {
                const isChecked = completionState[criterion] || false;
                return (
                  <div key={index} className="flex items-start gap-3">
                    <Checkbox
                      id={"criterion-" + index}
                      checked={isChecked}
                      onCheckedChange={function(checked) { handleCriteriaChange(criterion, checked); }}
                      className="mt-0.5"
                    />
                    <label 
                      htmlFor={"criterion-" + index}
                      className={"text-sm cursor-pointer " + (isChecked ? "text-slate-500 line-through" : "text-slate-700")}
                    >
                      {criterion}
                    </label>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Items Progress */}
        <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
              <FileText className="w-5 h-5 text-blue-600" />
              Progression des items
            </CardTitle>
            <CardDescription>
              {itemsCompletedCount}/{items.length} items complétés
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={(itemsCompletedCount / items.length) * 100} className="h-2 mb-4" />
            <div className="grid grid-cols-4 gap-4 text-center">
              <div className="p-2 bg-slate-50 rounded-lg">
                <p className="text-xl font-bold text-slate-900">
                  {items.filter(function(i) { return i.status === "not_started"; }).length}
                </p>
                <p className="text-xs text-slate-500">Non démarrés</p>
              </div>
              <div className="p-2 bg-amber-50 rounded-lg">
                <p className="text-xl font-bold text-amber-700">
                  {items.filter(function(i) { return i.status === "in_progress"; }).length}
                </p>
                <p className="text-xs text-slate-500">En cours</p>
              </div>
              <div className="p-2 bg-blue-50 rounded-lg">
                <p className="text-xl font-bold text-blue-700">
                  {items.filter(function(i) { return i.status === "done"; }).length}
                </p>
                <p className="text-xs text-slate-500">Terminés</p>
              </div>
              <div className="p-2 bg-emerald-50 rounded-lg">
                <p className="text-xl font-bold text-emerald-700">
                  {items.filter(function(i) { return i.status === "validated"; }).length}
                </p>
                <p className="text-xs text-slate-500">Validés</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Items List */}
      <Card className="border border-slate-200 shadow-sm animate-slide-in-up">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Items de l'atelier
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {items.map(function(item) {
              const statusBadge = getStatusBadge(item.status);
              const acceptanceState = item.acceptance_state || {};
              const acceptanceCriteria = item.acceptance_criteria || [];
              let acceptanceCompletedCount = 0;
              acceptanceCriteria.forEach(function(c) {
                if (acceptanceState[c]) acceptanceCompletedCount++;
              });
              
              return (
                <div 
                  key={item.item_id}
                  className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
                  onClick={function() { openItemDialog(item); }}
                >
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    <div className={`
                      w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold
                      ${item.status === "validated" 
                        ? "bg-emerald-100 text-emerald-700" 
                        : item.status === "done" 
                          ? "bg-blue-100 text-blue-700" 
                          : item.status === "in_progress"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-slate-200 text-slate-600"
                      }
                    `}>
                      {item.item_id}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-slate-900 truncate">{item.title}</h4>
                        <Badge variant="outline" className={"text-xs " + getRequirementBadge(item.status_requirement)}>
                          {item.status_requirement}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-500 truncate">{item.module_name}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 ml-4">
                    <div className="text-center w-20">
                      <Progress value={(acceptanceCompletedCount / acceptanceCriteria.length) * 100} className="h-1.5 mb-1" />
                      <p className="text-xs text-slate-500">{acceptanceCompletedCount}/{acceptanceCriteria.length}</p>
                    </div>
                    
                    {item.owner_user_id && (
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <User className="w-3 h-3" />
                        <span className="truncate max-w-[80px]">{item.owner_user_id}</span>
                      </div>
                    )}
                    
                    {item.due_date && (
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(item.due_date).toLocaleDateString("fr-FR")}</span>
                      </div>
                    )}
                    
                    <Badge className={statusBadge.className}>
                      {statusBadge.label}
                    </Badge>
                    
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Item Edit Dialog */}
      {selectedItem && (
        <Dialog open={itemDialogOpen} onOpenChange={setItemDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <span className="text-sm font-bold text-amber-600">{selectedItem.item_id}</span>
                {selectedItem.title}
              </DialogTitle>
            </DialogHeader>
            
            <ScrollArea className="flex-1 pr-4">
              <div className="space-y-6 py-4">
                {/* User Story */}
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                  <h4 className="font-medium text-blue-800 mb-2">User Story</h4>
                  <p className="text-sm text-blue-700">{selectedItem.user_story_fr}</p>
                </div>

                {/* Status & Owner */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Statut</Label>
                    <Select
                      value={selectedItem.status || "not_started"}
                      onValueChange={function(value) { setSelectedItem(function(prev) { return {...prev, status: value}; }); }}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="not_started">Non démarré</SelectItem>
                        <SelectItem value="in_progress">En cours</SelectItem>
                        <SelectItem value="done">Terminé</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Propriétaire</Label>
                    <Input
                      value={selectedItem.owner_user_id || ""}
                      onChange={function(e) { setSelectedItem(function(prev) { return {...prev, owner_user_id: e.target.value}; }); }}
                      placeholder="Nom ou ID"
                    />
                  </div>
                </div>

                {/* Due Date */}
                <div className="space-y-2">
                  <Label>Date d'échéance</Label>
                  <Input
                    type="date"
                    value={selectedItem.due_date ? selectedItem.due_date.split("T")[0] : ""}
                    onChange={function(e) { setSelectedItem(function(prev) { return {...prev, due_date: e.target.value}; }); }}
                  />
                </div>

                {/* Notes */}
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Textarea
                    value={selectedItem.notes_markdown || ""}
                    onChange={function(e) { setSelectedItem(function(prev) { return {...prev, notes_markdown: e.target.value}; }); }}
                    placeholder="Notes, commentaires, contexte..."
                    rows={4}
                  />
                </div>

                {/* Acceptance Criteria */}
                <div className="space-y-3">
                  <Label className="flex items-center gap-2">
                    <CheckCheck className="w-4 h-4 text-emerald-600" />
                    Critères d'acceptation
                  </Label>
                  <div className="space-y-2 p-4 bg-slate-50 rounded-lg">
                    {(selectedItem.acceptance_criteria || []).map(function(criterion, index) {
                      const isChecked = selectedItem.acceptance_state && selectedItem.acceptance_state[criterion];
                      return (
                        <div key={index} className="flex items-start gap-3">
                          <Checkbox
                            id={"acc-" + index}
                            checked={isChecked || false}
                            onCheckedChange={function(checked) { handleAcceptanceCriteriaChange(criterion, checked); }}
                            className="mt-0.5"
                          />
                          <label 
                            htmlFor={"acc-" + index}
                            className={"text-sm cursor-pointer " + (isChecked ? "text-slate-500 line-through" : "text-slate-700")}
                          >
                            {criterion}
                          </label>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Validation */}
                {selectedItem.status === "done" && (
                  <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-emerald-800">Validation</h4>
                        <p className="text-sm text-emerald-600">Marquer cet item comme validé</p>
                      </div>
                      <Button
                        onClick={function() { handleValidateItem(selectedItem.item_id, true); }}
                        className="bg-emerald-600 hover:bg-emerald-700"
                      >
                        <CheckCircle2 className="w-4 h-4 mr-2" />
                        Valider
                      </Button>
                    </div>
                  </div>
                )}

                {selectedItem.status === "validated" && (
                  <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-emerald-800 flex items-center gap-2">
                          <CheckCircle2 className="w-5 h-5" />
                          Item validé
                        </h4>
                        <p className="text-sm text-emerald-600">
                          Validé par {selectedItem.validated_by}
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        onClick={function() { handleValidateItem(selectedItem.item_id, false); }}
                      >
                        Retirer la validation
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <DialogFooter className="border-t pt-4">
              <Button variant="outline" onClick={function() { setItemDialogOpen(false); }}>
                Annuler
              </Button>
              <Button onClick={handleItemUpdate} disabled={saving} className="bg-amber-500 hover:bg-amber-600">
                {saving ? (
                  <span className="flex items-center">
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Enregistrement...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Save className="w-4 h-4 mr-2" />
                    Enregistrer
                  </span>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
