import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Trophy } from 'lucide-react';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function Leaderboard() {
  const { contestId } = useParams();
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, [contestId]);

  const fetchLeaderboard = async () => {
    try {
      const response = await api.get(`/contests/${contestId}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-3xl">Leaderboard</CardTitle>
              <div className="text-right">
                <p className="text-sm text-gray-600">Prize Pool</p>
                <p className="text-2xl font-bold text-green-600">${leaderboard?.prize_pool}</p>
              </div>
            </div>
            <p className="text-gray-600">{leaderboard?.total_entries} Participants</p>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">Rank</TableHead>
                  <TableHead>Username</TableHead>
                  <TableHead>Team Name</TableHead>
                  <TableHead className="text-right">Points</TableHead>
                  <TableHead className="text-right">Winnings</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leaderboard?.entries.map((entry) => {
                  const isCurrentUser = entry.user_id === user?.id;

                  return (
                    <TableRow key={entry.rank} className={isCurrentUser ? 'bg-green-50' : ''}>
                      <TableCell className="font-bold">
                        {entry.rank === 1 && <Trophy className="h-5 w-5 text-yellow-500 inline mr-1" />}
                        #{entry.rank}
                      </TableCell>
                      <TableCell>
                        {entry.username}
                        {isCurrentUser && <Badge className="ml-2" variant="secondary">You</Badge>}
                      </TableCell>
                      <TableCell>{entry.team_name}</TableCell>
                      <TableCell className="text-right font-semibold">{entry.total_points}</TableCell>
                      <TableCell className="text-right font-semibold text-green-600">
                        {entry.winnings > 0 ? `$${entry.winnings}` : '-'}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}