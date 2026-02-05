import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  ArrowLeft, 
  Plus,
  ListTodo,
  Calendar,
  User,
  Clock,
  Loader2,
  Trash2,
  Edit,
  AlertCircle,
  CheckCircle2
} from "lucide-react";

export default function PPActions() {
  const [loading, setLoading] = useState(true);
  const [actions, setActions] = useState([]);
  const [workshops, setWorkshops] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAction, setEditingAction] = useState(null);
  const [saving, setSaving] = useState(false);
  
  // Filters
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterPriority, setFilterPriority] = useState("all");
  const [filterWorkshop, setFilterWorkshop] = useState("all");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [actionsRes, workshopsRes] = await Promise.all([
        axios.get("/power-platform/actions"),
        axios.get("/power-platform/workshops")
      ]);
      setActions(actionsRes.data);
      setWorkshops(workshopsRes.data);
    } catch (error) {
      console.error("Error fetching actions:", error);
      toast.error("Erreur lors du chargement");
    } finally {
      setLoading(false);
    }
  };

  const openCreateDialog = () => {
    setEditingAction({
      title: "",
      description: "",
      priority: "medium",
      status: "open",
      workshop_number: null,
      owner_user_id: "",
      due_date: ""
    });
    setDialogOpen(true);
  };

  const openEditDialog = (action) => {
    setEditingAction({...action});
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!editingAction.title) {
      toast.error("Le titre est requis");
      return;
    }
    
    setSaving(true);
    try {
      if (editingAction.id) {
        // Update
        await axios.patch(`/power-platform/actions/${editingAction.id}`, {
          title: editingAction.title,
          description: editingAction.description,
          priority: editingAction.priority,
          status: editingAction.status,
          owner_user_id: editingAction.owner_user_id || null,
          due_date: editingAction.due_date || null
        });
        toast.success("Action mise à jour");
      } else {
        // Create
        await axios.post("/power-platform/actions", {
          title: editingAction.title,
          description: editingAction.description,
          priority: editingAction.priority,
          workshop_number: editingAction.workshop_number === "null" ? null : editingAction.workshop_number ? parseInt(editingAction.workshop_number) : null,
          owner_user_id: editingAction.owner_user_id || null,
          due_date: editingAction.due_date || null
        });
        toast.success("Action créée");
      }
      setDialogOpen(false);
      fetchData();
    } catch (error) {
      toast.error("Erreur lors de l'enregistrement");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (actionId) => {
    if (!confirm("Supprimer cette action ?")) return;
    
    try {
      await axios.delete(`/power-platform/actions/${actionId}`);
      toast.success("Action supprimée");
      fetchData();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case "critical": return { label: "Critique", className: "bg-red-100 text-red-700" };
      case "high": return { label: "Haute", className: "bg-orange-100 text-orange-700" };
      case "medium": return { label: "Moyenne", className: "bg-amber-100 text-amber-700" };
      case "low": return { label: "Basse", className: "bg-slate-100 text-slate-600" };
      default: return { label: priority, className: "bg-slate-100 text-slate-600" };
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "done": 
      case "closed": return { label: status === "done" ? "Terminé" : "Fermé", className: "bg-emerald-100 text-emerald-700" };
      case "in_progress": return { label: "En cours", className: "bg-blue-100 text-blue-700" };
      case "open": return { label: "Ouvert", className: "bg-amber-100 text-amber-700" };
      default: return { label: status, className: "bg-slate-100 text-slate-600" };
    }
  };

  const filteredActions = actions.filter(action => {
    if (filterStatus !== "all" && action.status !== filterStatus) return false;
    if (filterPriority !== "all" && action.priority !== filterPriority) return false;
    if (filterWorkshop !== "all") {
      if (filterWorkshop === "none" && action.workshop_number !== null) return false;
      if (filterWorkshop !== "none" && action.workshop_number !== parseInt(filterWorkshop)) return false;
    }
    return true;
  });

  const openActionsCount = actions.filter(a => a.status === "open" || a.status === "in_progress").length;
  const avgAgeing = actions.filter(a => a.status === "open" || a.status === "in_progress")
    .reduce((sum, a) => sum + (a.ageing_days || 0), 0) / (openActionsCount || 1);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="pp-actions-page">
      <Toaster position="top-right" richColors />

      {/* Header */}
      <div className="animate-fade-in">
        <Link to="/dashboards/power-platform" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Retour au programme
        </Link>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ListTodo className="w-8 h-8 text-amber-500" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Plan d'actions
              </h1>
              <p className="text-slate-500">
                {openActionsCount} actions ouvertes • Âge moyen: {Math.round(avgAgeing)} jours
              </p>
            </div>
          </div>
          <Button onClick={openCreateDialog} className="bg-amber-500 hover:bg-amber-600">
            <Plus className="w-4 h-4 mr-2" />
            Nouvelle action
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="border border-slate-200 shadow-sm">
        <CardContent className="py-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <Label className="text-sm text-slate-500">Statut:</Label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous</SelectItem>
                  <SelectItem value="open">Ouvert</SelectItem>
                  <SelectItem value="in_progress">En cours</SelectItem>
                  <SelectItem value="done">Terminé</SelectItem>
                  <SelectItem value="closed">Fermé</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center gap-2">
              <Label className="text-sm text-slate-500">Priorité:</Label>
              <Select value={filterPriority} onValueChange={setFilterPriority}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes</SelectItem>
                  <SelectItem value="critical">Critique</SelectItem>
                  <SelectItem value="high">Haute</SelectItem>
                  <SelectItem value="medium">Moyenne</SelectItem>
                  <SelectItem value="low">Basse</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center gap-2">
              <Label className="text-sm text-slate-500">Atelier:</Label>
              <Select value={filterWorkshop} onValueChange={setFilterWorkshop}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous</SelectItem>
                  <SelectItem value="none">Non lié</SelectItem>
                  {workshops.map(ws => (
                    <SelectItem key={ws.workshop_number} value={ws.workshop_number.toString()}>
                      Atelier {ws.workshop_number}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions Table */}
      <Card className="border border-slate-200 shadow-sm">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50">
                <TableHead className="font-semibold text-slate-600">Action</TableHead>
                <TableHead className="font-semibold text-slate-600">Atelier</TableHead>
                <TableHead className="font-semibold text-slate-600">Priorité</TableHead>
                <TableHead className="font-semibold text-slate-600">Propriétaire</TableHead>
                <TableHead className="font-semibold text-slate-600">Échéance</TableHead>
                <TableHead className="font-semibold text-slate-600 text-center">Âge</TableHead>
                <TableHead className="font-semibold text-slate-600">Statut</TableHead>
                <TableHead className="font-semibold text-slate-600 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredActions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-slate-500">
                    Aucune action trouvée
                  </TableCell>
                </TableRow>
              ) : (
                filteredActions.map((action) => {
                  const priorityBadge = getPriorityBadge(action.priority);
                  const statusBadge = getStatusBadge(action.status);
                  const isOverdue = action.due_date && new Date(action.due_date) < new Date() && action.status !== "done" && action.status !== "closed";
                  
                  return (
                    <TableRow key={action.id} className="hover:bg-slate-50">
                      <TableCell>
                        <div>
                          <p className="font-medium text-slate-900">{action.title}</p>
                          {action.description && (
                            <p className="text-sm text-slate-500 truncate max-w-xs">{action.description}</p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {action.workshop_number ? (
                          <Badge variant="outline">Atelier {action.workshop_number}</Badge>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge className={priorityBadge.className}>{priorityBadge.label}</Badge>
                      </TableCell>
                      <TableCell>
                        {action.owner_user_id ? (
                          <div className="flex items-center gap-1 text-sm">
                            <User className="w-3 h-3 text-slate-400" />
                            <span>{action.owner_user_id}</span>
                          </div>
                        ) : (
                          <span className="text-slate-400 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3 text-amber-500" />
                            Non assigné
                          </span>
                        )}
                      </TableCell>
                      <TableCell>
                        {action.due_date ? (
                          <div className={`flex items-center gap-1 text-sm ${isOverdue ? "text-red-600" : "text-slate-600"}`}>
                            <Calendar className="w-3 h-3" />
                            {new Date(action.due_date).toLocaleDateString("fr-FR")}
                            {isOverdue && <AlertCircle className="w-3 h-3 ml-1" />}
                          </div>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        <span className={`font-medium ${action.ageing_days > 30 ? "text-red-600" : action.ageing_days > 14 ? "text-amber-600" : "text-slate-600"}`}>
                          {action.ageing_days || 0}j
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge className={statusBadge.className}>{statusBadge.label}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="sm" onClick={() => openEditDialog(action)}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(action.id)} className="text-red-600 hover:text-red-700">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingAction?.id ? "Modifier l'action" : "Nouvelle action"}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Titre *</Label>
              <Input
                value={editingAction?.title || ""}
                onChange={(e) => setEditingAction(prev => ({...prev, title: e.target.value}))}
                placeholder="Titre de l'action"
              />
            </div>
            
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={editingAction?.description || ""}
                onChange={(e) => setEditingAction(prev => ({...prev, description: e.target.value}))}
                placeholder="Description détaillée"
                rows={3}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Priorité</Label>
                <Select
                  value={editingAction?.priority || "medium"}
                  onValueChange={(value) => setEditingAction(prev => ({...prev, priority: value}))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="critical">Critique</SelectItem>
                    <SelectItem value="high">Haute</SelectItem>
                    <SelectItem value="medium">Moyenne</SelectItem>
                    <SelectItem value="low">Basse</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {editingAction?.id && (
                <div className="space-y-2">
                  <Label>Statut</Label>
                  <Select
                    value={editingAction?.status || "open"}
                    onValueChange={(value) => setEditingAction(prev => ({...prev, status: value}))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="open">Ouvert</SelectItem>
                      <SelectItem value="in_progress">En cours</SelectItem>
                      <SelectItem value="done">Terminé</SelectItem>
                      <SelectItem value="closed">Fermé</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Atelier lié</Label>
                <Select
                  value={editingAction?.workshop_number?.toString() || "null"}
                  onValueChange={(value) => setEditingAction(prev => ({...prev, workshop_number: value}))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="null">Aucun</SelectItem>
                    {workshops.map(ws => (
                      <SelectItem key={ws.workshop_number} value={ws.workshop_number.toString()}>
                        Atelier {ws.workshop_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Propriétaire</Label>
                <Input
                  value={editingAction?.owner_user_id || ""}
                  onChange={(e) => setEditingAction(prev => ({...prev, owner_user_id: e.target.value}))}
                  placeholder="Nom ou ID"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Date d'échéance</Label>
              <Input
                type="date"
                value={editingAction?.due_date ? editingAction.due_date.split("T")[0] : ""}
                onChange={(e) => setEditingAction(prev => ({...prev, due_date: e.target.value}))}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleSave} disabled={saving} className="bg-amber-500 hover:bg-amber-600">
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Enregistrement...
                </>
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
