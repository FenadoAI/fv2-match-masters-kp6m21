import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Trophy, Users, DollarSign, TrendingUp } from 'lucide-react';
import api from '../utils/api';

export default function Landing() {
  const [contests, setContests] = useState([]);

  useEffect(() => {
    fetchFeaturedContests();
  }, []);

  const fetchFeaturedContests = async () => {
    try {
      const response = await api.get('/contests');
      setContests(response.data.contests.slice(0, 3));
    } catch (error) {
      console.error('Failed to fetch contests:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-green-600 to-blue-600 text-white py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Play Fantasy Cricket, Win Real Cash
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-green-50">
            Create your dream team, join contests, and compete with millions
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button size="lg" className="bg-white text-green-600 hover:bg-gray-100 text-lg px-8 py-6">
                Start Playing Now
              </Button>
            </Link>
            <Link to="/contests">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/20 text-lg px-8 py-6">
                Browse Contests
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="max-w-6xl mx-auto py-16 px-4">
        <h2 className="text-4xl font-bold text-center mb-12 text-gray-900">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="bg-green-100 p-4 rounded-full">
                  <Users className="h-8 w-8 text-green-600" />
                </div>
              </div>
              <CardTitle>Create Your Team</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Pick 11 players within your 100 credit budget. Choose your captain and vice-captain wisely for bonus points!
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="bg-blue-100 p-4 rounded-full">
                  <Trophy className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <CardTitle>Join Contests</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Enter paid contests with your team. Choose from mega contests or smaller leagues based on your preference.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="bg-yellow-100 p-4 rounded-full">
                  <DollarSign className="h-8 w-8 text-yellow-600" />
                </div>
              </div>
              <CardTitle>Win Prizes</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Watch the match live as your players score points. Climb the leaderboard and win real cash prizes!
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Featured Contests */}
      {contests.length > 0 && (
        <div className="max-w-6xl mx-auto py-16 px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-4xl font-bold text-gray-900">Featured Contests</h2>
            <Link to="/contests">
              <Button variant="outline">View All</Button>
            </Link>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {contests.map((contest) => (
              <Card key={contest.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle>{contest.name}</CardTitle>
                  <CardDescription>Entry Fee: ${contest.entry_fee}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Prize Pool</span>
                      <span className="font-semibold text-green-600">${contest.prize_pool}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Spots</span>
                      <span className="font-semibold">{contest.joined_users}/{contest.max_users}</span>
                    </div>
                  </div>
                  <Link to="/contests">
                    <Button className="w-full mt-4 bg-green-600 hover:bg-green-700">Join Now</Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Stats Section */}
      <div className="bg-green-600 text-white py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <TrendingUp className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-4xl font-bold mb-2">$1M+</h3>
              <p className="text-green-100">Prize Money Distributed</p>
            </div>
            <div>
              <Users className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-4xl font-bold mb-2">10K+</h3>
              <p className="text-green-100">Active Players</p>
            </div>
            <div>
              <Trophy className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-4xl font-bold mb-2">500+</h3>
              <p className="text-green-100">Daily Contests</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}