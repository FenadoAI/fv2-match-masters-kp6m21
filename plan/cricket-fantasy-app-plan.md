# Cricket Fantasy Sports App - Implementation Plan

## Overview
Build a complete cricket fantasy sports platform with public paid contests, team management, live scoring, and automated payouts.

## Phase 1: Backend Foundation (APIs First)

### 1.1 Database Schema Design
- **users**: id, username, email, password_hash, wallet_balance, created_at
- **matches**: id, title, team1, team2, start_time, status, venue, match_type
- **contests**: id, match_id, entry_fee, prize_pool, max_users, joined_users, status
- **teams**: id, user_id, contest_id, match_id, players[], captain_id, vice_captain_id, total_points
- **players**: id, name, role, team, base_price, current_points, match_id
- **contest_entries**: id, contest_id, user_id, team_id, rank, winnings
- **transactions**: id, user_id, type, amount, status, reference_id

### 1.2 Core Backend APIs
1. **Authentication APIs**
   - POST /api/auth/register
   - POST /api/auth/login
   - GET /api/auth/profile

2. **Match APIs**
   - GET /api/matches (upcoming matches)
   - GET /api/matches/:id

3. **Contest APIs**
   - GET /api/contests (list all public contests)
   - GET /api/contests/:id
   - POST /api/contests/:id/join (pay entry fee and join)

4. **Team APIs**
   - GET /api/players/:match_id (get available players)
   - POST /api/teams (create fantasy team)
   - GET /api/teams/:id
   - GET /api/teams/user/:user_id

5. **Payment APIs**
   - POST /api/payments/add-funds (Stripe integration)
   - GET /api/wallet/balance

6. **Leaderboard APIs**
   - GET /api/contests/:id/leaderboard

### 1.3 Environment Variables
- STRIPE_API_KEY (to be added)
- CRICKET_API_KEY (to be added - for live data)
- CRICKET_API_BASE_URL

## Phase 2: Frontend Implementation

### 2.1 Pages & Routes
1. **Landing Page** (/)
   - Hero section with app overview
   - Featured contests
   - How it works section
   - CTA to sign up

2. **Auth Pages** (/login, /register)
   - Login form
   - Registration form

3. **Contest Lobby** (/contests)
   - List all public contests
   - Filter by match, entry fee
   - Join contest button

4. **Team Creation** (/create-team/:match_id/:contest_id)
   - Player selection interface
   - Budget management (100 credits)
   - Captain/Vice-captain selection
   - Role-based filters (Batsman, Bowler, All-rounder, Wicket-keeper)

5. **My Contests** (/my-contests)
   - List of joined contests
   - Live scoring updates
   - Contest status

6. **Leaderboard** (/contest/:id/leaderboard)
   - Live rankings
   - User team details
   - Prize distribution

7. **Wallet** (/wallet)
   - Current balance
   - Add funds via Stripe
   - Transaction history

### 2.2 Key Components
- ContestCard (display contest info)
- PlayerCard (for team selection)
- LeaderboardTable
- TeamSummary
- WalletBalance
- PaymentModal (Stripe integration)

## Phase 3: Payment Integration

### 3.1 Stripe Setup
- Create Stripe account
- Add STRIPE_API_KEY to backend/.env
- Implement payment flow for adding funds to wallet
- Contest entry uses wallet balance (no direct Stripe charge per contest)

### 3.2 Payment Flow
1. User adds funds to wallet via Stripe
2. Funds are credited to user's wallet_balance
3. Joining contest deducts entry_fee from wallet_balance
4. Winners receive payouts in wallet_balance
5. Users can withdraw to bank (future enhancement)

## Phase 4: Point Calculation System

### 4.1 Cricket Scoring Rules
- **Batting**: Runs (1 pt/run), 4s (1 bonus), 6s (2 bonus), 50 runs (8 bonus), 100 runs (16 bonus)
- **Bowling**: Wicket (25 pts), Maiden (12 pts), 3 wickets (4 bonus), 5 wickets (8 bonus)
- **Fielding**: Catch (8 pts), Stumping (12 pts), Run out (6 pts)
- **Captain**: 2x points
- **Vice-Captain**: 1.5x points

### 4.2 Implementation
- Background job to fetch live scores from Cricket API
- Update player points in real-time
- Recalculate team total_points
- Update contest rankings

## Phase 5: Winner Calculation & Payout

### 5.1 Contest Completion Flow
1. Match ends → Contest status = "completed"
2. Final rankings calculated
3. Prize distribution based on rank
4. Winners' wallets credited automatically
5. Notification to winners

## Testing Strategy

### Backend Testing
- Test all APIs with running server
- Verify payment flow with Stripe test mode
- Test point calculation logic
- Test contest join/leave flows

### Frontend Testing
- Build frontend (`bun run build`)
- Test all user flows end-to-end
- Verify responsive design
- Test payment integration

## Success Criteria
✅ User can register/login
✅ User can view upcoming matches and contests
✅ User can add funds via Stripe
✅ User can create fantasy team within budget
✅ User can join paid contest
✅ Live leaderboard updates during match
✅ Accurate point calculation
✅ Automated winner payout

## Implementation Order
1. ✅ Create implementation plan
2. Backend: Database models and core APIs
3. Backend: Payment integration (Stripe)
4. Backend: Team creation and validation logic
5. Test all backend APIs
6. Frontend: Landing page and auth
7. Frontend: Contest lobby
8. Frontend: Team creation interface
9. Frontend: Leaderboard and live scoring
10. Frontend: Wallet and payment integration
11. Build and deploy
12. End-to-end testing