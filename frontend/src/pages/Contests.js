import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Trophy, Users, DollarSign } from 'lucide-react';
import api from '../utils/api';

export default function Contests() {
  const [contests, setContests] = useState([]);
  const [matches, setMatches] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [contestsRes, matchesRes] = await Promise.all([
        api.get('/contests'),
        api.get('/matches')
      ]);

      setContests(contestsRes.data.contests);

      const matchesMap = {};
      matchesRes.data.matches.forEach(match => {
        matchesMap[match.id] = match;
      });
      setMatches(matchesMap);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">All Contests</h1>
          <p className="text-gray-600">Choose your contest and start winning</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {contests.map((contest) => {
            const match = matches[contest.match_id];
            const spotsLeft = contest.max_users - contest.joined_users;

            return (
              <Card key={contest.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start mb-2">
                    <Badge variant={contest.status === 'open' ? 'default' : 'secondary'}>
                      {contest.status}
                    </Badge>
                    <Trophy className="h-5 w-5 text-yellow-500" />
                  </div>
                  <CardTitle className="text-xl">{contest.name}</CardTitle>
                  <CardDescription>
                    {match ? `${match.team1} vs ${match.team2}` : 'Loading match...'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Entry Fee</span>
                      <span className="font-bold text-lg text-green-600">${contest.entry_fee}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Prize Pool</span>
                      <span className="font-semibold flex items-center">
                        <DollarSign className="h-4 w-4 text-yellow-500" />
                        {contest.prize_pool}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Spots Left</span>
                      <span className="font-semibold flex items-center">
                        <Users className="h-4 w-4 mr-1" />
                        {spotsLeft}/{contest.max_users}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${(contest.joined_users / contest.max_users) * 100}%` }}
                      />
                    </div>
                    <Link to={`/create-team/${contest.match_id}/${contest.id}`}>
                      <Button className="w-full bg-green-600 hover:bg-green-700 mt-2">
                        Join Contest
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}