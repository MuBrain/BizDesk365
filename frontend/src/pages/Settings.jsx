import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Toaster, toast } from "sonner";
import { Settings as SettingsIcon, ShieldCheck, Bot, Save, Loader2, Info } from "lucide-react";

export default function Settings() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isoProfiles, setIsoProfiles] = useState([]);
  const [aiPolicy, setAiPolicy] = useState({
    min_iqi_authorized: 0.80,
    min_iqi_assisted: 0.60
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [isoRes, policyRes] = await Promise.all([
        axios.get("/settings/iso"),
        axios.get("/settings/ai-policy")
      ]);
      setIsoProfiles(isoRes.data);
      setAiPolicy(policyRes.data);
    } catch (error) {
      console.error("Error fetching settings:", error);
      toast.error("Erreur lors du chargement des paramètres");
    } finally {
      setLoading(false);
    }
  };

  const handleISOToggle = (isoCode, enabled) => {
    setIsoProfiles(prev => 
      prev.map(profile => 
        profile.iso_code === isoCode 
          ? { ...profile, enabled } 
          : profile
      )
    );
  };

  const saveISOProfiles = async () => {
    setSaving(true);
    try {
      await axios.put("/settings/iso", { profiles: isoProfiles });
      toast.success("Profils ISO enregistrés avec succès");
    } catch (error) {
      console.error("Error saving ISO profiles:", error);
      toast.error("Erreur lors de l'enregistrement des profils ISO");
    } finally {
      setSaving(false);
    }
  };

  const saveAIPolicy = async () => {
    if (aiPolicy.min_iqi_authorized < aiPolicy.min_iqi_assisted) {
      toast.error("Le seuil autorisé doit être supérieur au seuil assisté");
      return;
    }
    
    setSaving(true);
    try {
      await axios.put("/settings/ai-policy", aiPolicy);
      toast.success("Politique IA enregistrée avec succès");
    } catch (error) {
      console.error("Error saving AI policy:", error);
      toast.error(error.response?.data?.detail || "Erreur lors de l'enregistrement de la politique IA");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="settings-page">
      <Toaster position="top-right" richColors />
      
      {/* Page header */}
      <div className="animate-fade-in">
        <div className="flex items-center gap-3 mb-1">
          <SettingsIcon className="w-8 h-8 text-slate-600" />
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Paramètres
          </h1>
        </div>
        <p className="text-slate-500">
          Configuration de votre organisation
        </p>
      </div>

      <Tabs defaultValue="iso" className="space-y-6">
        <TabsList className="bg-slate-100">
          <TabsTrigger value="iso" className="data-[state=active]:bg-white">
            <ShieldCheck className="w-4 h-4 mr-2" />
            Référentiels ISO
          </TabsTrigger>
          <TabsTrigger value="ai" className="data-[state=active]:bg-white">
            <Bot className="w-4 h-4 mr-2" />
            Politique IA
          </TabsTrigger>
        </TabsList>

        {/* ISO Settings Tab */}
        <TabsContent value="iso" className="animate-fade-in">
          <Card className="border border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Référentiels ISO
              </CardTitle>
              <CardDescription>
                Activez les normes ISO applicables à votre organisation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                {isoProfiles.map((profile) => (
                  <div 
                    key={profile.iso_code}
                    className={`flex items-center justify-between p-4 rounded-lg border transition-colors ${
                      profile.enabled 
                        ? 'bg-blue-50 border-blue-200' 
                        : 'bg-slate-50 border-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        profile.enabled ? 'bg-blue-100' : 'bg-slate-200'
                      }`}>
                        <ShieldCheck className={`w-5 h-5 ${
                          profile.enabled ? 'text-blue-600' : 'text-slate-400'
                        }`} />
                      </div>
                      <div>
                        <p className="font-medium text-slate-900">{profile.iso_code}</p>
                        <p className="text-sm text-slate-500">{profile.name}</p>
                      </div>
                    </div>
                    <Switch
                      checked={profile.enabled}
                      onCheckedChange={(checked) => handleISOToggle(profile.iso_code, checked)}
                      data-testid={`iso-toggle-${profile.iso_code}`}
                    />
                  </div>
                ))}
              </div>

              <div className="flex justify-end pt-4 border-t border-slate-200">
                <Button 
                  onClick={saveISOProfiles}
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700"
                  data-testid="save-iso-btn"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Enregistrement...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Enregistrer
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Policy Tab */}
        <TabsContent value="ai" className="animate-fade-in">
          <Card className="border border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Politique d'utilisation IA
              </CardTitle>
              <CardDescription>
                Définissez les seuils IQI pour autoriser l'utilisation de l'IA
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-8">
              {/* Info box */}
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div className="text-sm text-slate-700">
                    <p className="font-medium text-blue-700 mb-1">Comment ça fonctionne ?</p>
                    <ul className="space-y-1 text-slate-600">
                      <li>• <strong>IA Autorisée</strong>: IQI ≥ seuil autorisé ET document validé</li>
                      <li>• <strong>IA Assistée</strong>: IQI ≥ seuil assisté (supervision requise)</li>
                      <li>• <strong>IA Interdite</strong>: IQI {"<"} seuil assisté</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Authorized threshold */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-base font-medium">Seuil IQI - IA Autorisée</Label>
                    <p className="text-sm text-slate-500 mt-0.5">
                      Score minimum pour une utilisation sans restriction
                    </p>
                  </div>
                  <Badge className="bg-emerald-100 text-emerald-700 border-0 text-lg px-4 py-1">
                    {Math.round(aiPolicy.min_iqi_authorized * 100)}%
                  </Badge>
                </div>
                <Slider
                  value={[aiPolicy.min_iqi_authorized * 100]}
                  onValueChange={([value]) => setAiPolicy(prev => ({ 
                    ...prev, 
                    min_iqi_authorized: value / 100 
                  }))}
                  max={100}
                  min={0}
                  step={5}
                  className="[&_[role=slider]]:bg-emerald-600"
                  data-testid="slider-authorized"
                />
                <div className="flex justify-between text-xs text-slate-400">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>

              {/* Assisted threshold */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-base font-medium">Seuil IQI - IA Assistée</Label>
                    <p className="text-sm text-slate-500 mt-0.5">
                      Score minimum pour une utilisation avec supervision
                    </p>
                  </div>
                  <Badge className="bg-amber-100 text-amber-700 border-0 text-lg px-4 py-1">
                    {Math.round(aiPolicy.min_iqi_assisted * 100)}%
                  </Badge>
                </div>
                <Slider
                  value={[aiPolicy.min_iqi_assisted * 100]}
                  onValueChange={([value]) => setAiPolicy(prev => ({ 
                    ...prev, 
                    min_iqi_assisted: value / 100 
                  }))}
                  max={100}
                  min={0}
                  step={5}
                  className="[&_[role=slider]]:bg-amber-600"
                  data-testid="slider-assisted"
                />
                <div className="flex justify-between text-xs text-slate-400">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>

              {/* Visual representation */}
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-sm font-medium text-slate-700 mb-3">Aperçu des zones</p>
                <div className="relative h-8 rounded-full overflow-hidden bg-slate-200">
                  <div 
                    className="absolute inset-y-0 left-0 bg-red-400"
                    style={{ width: `${aiPolicy.min_iqi_assisted * 100}%` }}
                  />
                  <div 
                    className="absolute inset-y-0 bg-amber-400"
                    style={{ 
                      left: `${aiPolicy.min_iqi_assisted * 100}%`,
                      width: `${(aiPolicy.min_iqi_authorized - aiPolicy.min_iqi_assisted) * 100}%`
                    }}
                  />
                  <div 
                    className="absolute inset-y-0 right-0 bg-emerald-400"
                    style={{ width: `${(1 - aiPolicy.min_iqi_authorized) * 100}%` }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-xs">
                  <span className="text-red-600">Interdit</span>
                  <span className="text-amber-600">Assisté</span>
                  <span className="text-emerald-600">Autorisé</span>
                </div>
              </div>

              <div className="flex justify-end pt-4 border-t border-slate-200">
                <Button 
                  onClick={saveAIPolicy}
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700"
                  data-testid="save-ai-policy-btn"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Enregistrement...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Enregistrer
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
