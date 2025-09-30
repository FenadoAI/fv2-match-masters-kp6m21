import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Trophy } from 'lucide-react';
import api from '../utils/api';

export default function MyContests() {
  const [myContests, setMyContests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMyContests();
  }, []);

  const fetchMyContests = async () => {
    try {
      const response = await api.get('/my-contests');
      setMyContests(response.data.my_contests);
    } catch (error) {
      console.error('Failed to fetch contests:', error);
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
        <h1 className="text-4xl font-bold mb-8">My Contests</h1>

        {myContests.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Trophy className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-semibold mb-2">No Contests Yet</h3>
              <p className="text-gray-600 mb-4">Join a contest to start playing</p>
              <Link to="/contests">
                <Button className="bg-green-600 hover:bg-green-700">Browse Contests</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {myContests.map(({ contest, match, entry, team }) => (
              <Card key={contest.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle>{contest.name}</CardTitle>
                      <CardDescription>
                        {match ? `${match.team1} vs ${match.team2}` : 'Match info unavailable'}
                      </CardDescription>
                    </div>
                    <Badge>{contest.status}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Team</p>
                      <p className="font-semibold">{team?.team_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Entry Fee</p>
                      <p className="font-semibold">${contest.entry_fee}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Prize Pool</p>
                      <p className="font-semibold text-green-600">${contest.prize_pool}</p>
                    </div>
                    <div>
                      <Link to={`/leaderboard/${contest.id}`}>
                        <Button variant="outline" className="w-full">View Leaderboard</Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}