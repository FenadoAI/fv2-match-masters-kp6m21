import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import api from '../utils/api';
import { useToast } from '../hooks/use-toast';

export default function CreateTeam() {
  const { matchId, contestId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [players, setPlayers] = useState([]);
  const [selectedPlayers, setSelectedPlayers] = useState([]);
  const [captain, setCaptain] = useState(null);
  const [viceCaptain, setViceCaptain] = useState(null);
  const [teamName, setTeamName] = useState('My Warriors');
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchPlayers();
  }, [matchId]);

  const fetchPlayers = async () => {
    try {
      const response = await api.get(`/players/${matchId}`);
      setPlayers(response.data.players);
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to load players', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const togglePlayer = (player) => {
    if (selectedPlayers.find(p => p.id === player.id)) {
      setSelectedPlayers(selectedPlayers.filter(p => p.id !== player.id));
      if (captain?.id === player.id) setCaptain(null);
      if (viceCaptain?.id === player.id) setViceCaptain(null);
    } else if (selectedPlayers.length < 11) {
      setSelectedPlayers([...selectedPlayers, player]);
    }
  };

  const totalCredits = selectedPlayers.reduce((sum, p) => sum + p.base_price, 0);
  const creditsLeft = 100 - totalCredits;

  const handleSubmit = async () => {
    if (selectedPlayers.length !== 11) {
      toast({ title: 'Error', description: 'Select exactly 11 players', variant: 'destructive' });
      return;
    }
    if (!captain || !viceCaptain) {
      toast({ title: 'Error', description: 'Select captain and vice-captain', variant: 'destructive' });
      return;
    }

    try {
      const teamPayload = {
        match_id: matchId,
        team_name: teamName,
        players: selectedPlayers.map(p => ({
          player_id: p.id,
          is_captain: p.id === captain?.id,
          is_vice_captain: p.id === viceCaptain?.id
        }))
      };

      const teamResponse = await api.post('/teams', teamPayload);
      await api.post(`/contests/${contestId}/join`, {
        contest_id: contestId,
        team_id: teamResponse.data.id
      });

      toast({ title: 'Success', description: 'Team created and contest joined!' });
      navigate('/my-contests');
    } catch (error) {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed to create team', variant: 'destructive' });
    }
  };

  const filteredPlayers = filter === 'all' ? players : players.filter(p => p.role === filter);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-6">
          <Label>Team Name</Label>
          <Input value={teamName} onChange={(e) => setTeamName(e.target.value)} className="max-w-md" />
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-6">
                <Tabs value={filter} onValueChange={setFilter}>
                  <TabsList>
                    <TabsTrigger value="all">All</TabsTrigger>
                    <TabsTrigger value="batsman">Batsmen</TabsTrigger>
                    <TabsTrigger value="bowler">Bowlers</TabsTrigger>
                    <TabsTrigger value="all_rounder">All-Rounders</TabsTrigger>
                    <TabsTrigger value="wicket_keeper">Keepers</TabsTrigger>
                  </TabsList>
                  <TabsContent value={filter} className="mt-4">
                    <div className="space-y-2">
                      {filteredPlayers.map(player => {
                        const isSelected = selectedPlayers.find(p => p.id === player.id);
                        const isCaptain = captain?.id === player.id;
                        const isViceCaptain = viceCaptain?.id === player.id;

                        return (
                          <div key={player.id} className={`flex items-center justify-between p-3 border rounded-lg ${isSelected ? 'bg-green-50 border-green-500' : 'hover:bg-gray-50'}`}>
                            <div className="flex items-center space-x-3">
                              <input type="checkbox" checked={!!isSelected} onChange={() => togglePlayer(player)} disabled={!isSelected && selectedPlayers.length >= 11} />
                              <div>
                                <p className="font-semibold">{player.name}</p>
                                <div className="flex gap-2">
                                  <Badge variant="outline">{player.role}</Badge>
                                  <Badge>{player.team}</Badge>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold">{player.base_price} cr</span>
                              {isSelected && (
                                <div className="flex gap-1">
                                  <Button size="sm" variant={isCaptain ? 'default' : 'outline'} onClick={() => setCaptain(player)}>C</Button>
                                  <Button size="sm" variant={isViceCaptain ? 'default' : 'outline'} onClick={() => setViceCaptain(player)}>VC</Button>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card className="sticky top-20">
              <CardContent className="p-6">
                <h3 className="font-bold text-lg mb-4">Team Summary</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Players</span>
                    <span className="font-bold">{selectedPlayers.length}/11</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Credits Left</span>
                    <span className={`font-bold ${creditsLeft < 0 ? 'text-red-600' : 'text-green-600'}`}>{creditsLeft.toFixed(1)}</span>
                  </div>
                  {captain && <Alert><AlertDescription>Captain: {captain.name} (2x points)</AlertDescription></Alert>}
                  {viceCaptain && <Alert><AlertDescription>Vice-Captain: {viceCaptain.name} (1.5x points)</AlertDescription></Alert>}
                  <Button className="w-full bg-green-600 hover:bg-green-700" onClick={handleSubmit} disabled={selectedPlayers.length !== 11 || !captain || !viceCaptain || creditsLeft < 0}>
                    Create Team & Join Contest
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}