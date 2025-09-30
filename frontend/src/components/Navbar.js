import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Trophy, Home, List, Calendar, Wallet, User, LogOut } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <div className="bg-green-600 p-2 rounded-lg">
                <Trophy className="h-6 w-6 text-white" />
              </div>
              <span className="font-bold text-xl text-gray-900">CricFantasy</span>
            </Link>

            {isAuthenticated && (
              <div className="hidden md:flex space-x-4">
                <Link to="/">
                  <Button variant={isActive('/') ? 'default' : 'ghost'} size="sm" className="flex items-center space-x-2">
                    <Home className="h-4 w-4" />
                    <span>Home</span>
                  </Button>
                </Link>
                <Link to="/contests">
                  <Button variant={isActive('/contests') ? 'default' : 'ghost'} size="sm" className="flex items-center space-x-2">
                    <List className="h-4 w-4" />
                    <span>Contests</span>
                  </Button>
                </Link>
                <Link to="/my-contests">
                  <Button variant={isActive('/my-contests') ? 'default' : 'ghost'} size="sm" className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4" />
                    <span>My Contests</span>
                  </Button>
                </Link>
                <Link to="/wallet">
                  <Button variant={isActive('/wallet') ? 'default' : 'ghost'} size="sm" className="flex items-center space-x-2">
                    <Wallet className="h-4 w-4" />
                    <span>Wallet</span>
                  </Button>
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <div className="hidden md:flex items-center space-x-2 bg-green-50 px-4 py-2 rounded-lg">
                  <Wallet className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-semibold text-green-700">${user?.wallet_balance?.toFixed(2) || '0.00'}</span>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                      <User className="h-4 w-4" />
                      <span className="hidden md:inline">{user?.username}</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>My Account</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link to="/wallet" className="flex items-center w-full">
                        <Wallet className="h-4 w-4 mr-2" />
                        Wallet
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logout} className="text-red-600">
                      <LogOut className="h-4 w-4 mr-2" />
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm">Login</Button>
                </Link>
                <Link to="/register">
                  <Button variant="default" size="sm" className="bg-green-600 hover:bg-green-700">Sign Up</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}