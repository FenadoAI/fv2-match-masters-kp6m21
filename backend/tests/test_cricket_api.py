"""Test cricket fantasy API endpoints."""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8001")
API_URL = f"{API_BASE}/api"


class TestState:
    """Shared state across tests."""

    access_token = None
    user_id = None
    match_id = None
    team_id = None
    contest_id = None


def test_register_user():
    """Test user registration."""
    print("\n🧪 Testing user registration...")

    response = requests.post(
        f"{API_URL}/auth/register",
        json={"username": "testuser123", "email": "testuser123@example.com", "password": "password123"},
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "access_token" in data, "Response should contain access_token"
    assert "user" in data, "Response should contain user data"
    assert data["user"]["username"] == "testuser123", "Username should match"

    # Save token for subsequent tests
    TestState.access_token = data["access_token"]
    TestState.user_id = data["user"]["id"]

    print(f"✅ User registered successfully: {data['user']['username']}")
    print(f"   Token: {TestState.access_token[:20]}...")


def test_login_user():
    """Test user login."""
    print("\n🧪 Testing user login...")

    response = requests.post(f"{API_URL}/auth/login", json={"username": "testuser123", "password": "password123"})

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "access_token" in data, "Response should contain access_token"
    assert data["user"]["username"] == "testuser123", "Username should match"

    print(f"✅ User logged in successfully: {data['user']['username']}")


def test_get_profile():
    """Test getting user profile with authentication."""
    print("\n🧪 Testing get profile...")

    headers = {"Authorization": f"Bearer {TestState.access_token}"}
    response = requests.get(f"{API_URL}/auth/profile", headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["username"] == "testuser123", "Username should match"
    assert "wallet_balance" in data, "Should have wallet_balance"

    print(f"✅ Profile retrieved: {data['username']}, Balance: ${data['wallet_balance']}")


def test_get_matches():
    """Test getting list of matches."""
    print("\n🧪 Testing get matches...")

    response = requests.get(f"{API_URL}/matches")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "matches" in data, "Response should contain matches list"
    assert len(data["matches"]) > 0, "Should have at least one match"

    # Save first match ID for subsequent tests
    TestState.match_id = data["matches"][0]["id"]

    print(f"✅ Found {len(data['matches'])} matches")
    print(f"   First match: {data['matches'][0]['title']}")


def test_get_players_for_match():
    """Test getting players for a specific match."""
    print("\n🧪 Testing get players for match...")

    response = requests.get(f"{API_URL}/players/{TestState.match_id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "players" in data, "Response should contain players list"
    assert len(data["players"]) >= 11, "Should have at least 11 players for team creation"

    print(f"✅ Found {len(data['players'])} players for match")


def test_get_contests():
    """Test getting list of contests."""
    print("\n🧪 Testing get contests...")

    response = requests.get(f"{API_URL}/contests")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "contests" in data, "Response should contain contests list"
    assert len(data["contests"]) > 0, "Should have at least one contest"

    # Save first contest for subsequent tests
    TestState.contest_id = data["contests"][0]["id"]

    print(f"✅ Found {len(data['contests'])} contests")
    print(f"   First contest: {data['contests'][0]['name']}, Entry: ${data['contests'][0]['entry_fee']}")


def test_add_funds_to_wallet():
    """Test adding funds to wallet."""
    print("\n🧪 Testing add funds to wallet...")

    headers = {"Authorization": f"Bearer {TestState.access_token}"}
    response = requests.post(
        f"{API_URL}/wallet/add-funds",
        headers=headers,
        json={"amount": 500.0, "payment_method_id": "pm_test_123"},
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["success"] is True, "Add funds should succeed"
    assert data["new_balance"] == 500.0, f"New balance should be 500.0, got {data['new_balance']}"

    print(f"✅ Added $500 to wallet. New balance: ${data['new_balance']}")


def test_create_team():
    """Test creating a fantasy team."""
    print("\n🧪 Testing create team...")

    # Get players for the match first
    response = requests.get(f"{API_URL}/players/{TestState.match_id}")
    players_data = response.json()
    all_players = players_data["players"]

    # Select 11 players within budget (100 credits)
    # Strategy: Pick mix of roles
    selected_players = []
    budget_remaining = 100.0

    # Get players by role
    wicket_keepers = [p for p in all_players if p["role"] == "wicket_keeper"]
    batsmen = [p for p in all_players if p["role"] == "batsman"]
    all_rounders = [p for p in all_players if p["role"] == "all_rounder"]
    bowlers = [p for p in all_players if p["role"] == "bowler"]

    # Select: 1 WK, 4 Batsmen, 3 All-rounders, 3 Bowlers
    team_composition = [
        (wicket_keepers, 1),
        (batsmen, 4),
        (all_rounders, 3),
        (bowlers, 3),
    ]

    for player_list, count in team_composition:
        # Sort by price (ascending) and pick cheapest
        sorted_players = sorted(player_list, key=lambda x: x["base_price"])
        for i in range(min(count, len(sorted_players))):
            player = sorted_players[i]
            if player["base_price"] <= budget_remaining:
                selected_players.append(player)
                budget_remaining -= player["base_price"]

    assert len(selected_players) == 11, f"Should have 11 players, got {len(selected_players)}"

    # Create team payload
    team_players = [{"player_id": p["id"], "is_captain": False, "is_vice_captain": False} for p in selected_players]

    # Set captain and vice-captain (first two players)
    team_players[0]["is_captain"] = True
    team_players[1]["is_vice_captain"] = True

    headers = {"Authorization": f"Bearer {TestState.access_token}"}
    response = requests.post(
        f"{API_URL}/teams",
        headers=headers,
        json={"match_id": TestState.match_id, "team_name": "Test Warriors", "players": team_players},
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["team_name"] == "Test Warriors", "Team name should match"
    assert len(data["players"]) == 11, "Should have 11 players"

    TestState.team_id = data["id"]

    print(f"✅ Team created: {data['team_name']}, Budget used: {100 - budget_remaining:.1f}/100 credits")


def test_join_contest():
    """Test joining a contest with a team."""
    print("\n🧪 Testing join contest...")

    headers = {"Authorization": f"Bearer {TestState.access_token}"}

    # Find a contest for the same match
    response = requests.get(f"{API_URL}/contests?match_id={TestState.match_id}")
    contests = response.json()["contests"]

    if not contests:
        print("⚠️  No contests available for this match, skipping test")
        return

    contest = contests[0]
    TestState.contest_id = contest["id"]

    # Join contest
    response = requests.post(
        f"{API_URL}/contests/{TestState.contest_id}/join",
        headers=headers,
        json={"contest_id": TestState.contest_id, "team_id": TestState.team_id},
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["success"] is True, "Join contest should succeed"

    print(f"✅ Successfully joined contest: {contest['name']}")


def test_get_wallet_balance():
    """Test getting wallet balance."""
    print("\n🧪 Testing get wallet balance...")

    headers = {"Authorization": f"Bearer {TestState.access_token}"}
    response = requests.get(f"{API_URL}/wallet/balance", headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "balance" in data, "Response should contain balance"

    # Balance should be reduced after joining contest
    expected_balance = 500.0 - 50.0  # Added 500, contest entry was probably 50 or less
    assert data["balance"] < 500.0, f"Balance should be less than 500 after joining contest, got {data['balance']}"

    print(f"✅ Current wallet balance: ${data['balance']}")


def test_get_my_contests():
    """Test getting user's joined contests."""
    print("\n🧪 Testing get my contests...")

    headers = {"Authorization": f"Bearer {TestState.access_token}"}
    response = requests.get(f"{API_URL}/my-contests", headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "my_contests" in data, "Response should contain my_contests"
    assert len(data["my_contests"]) > 0, "Should have at least one contest"

    print(f"✅ User has joined {len(data['my_contests'])} contests")


def test_get_leaderboard():
    """Test getting contest leaderboard."""
    print("\n🧪 Testing get contest leaderboard...")

    response = requests.get(f"{API_URL}/contests/{TestState.contest_id}/leaderboard")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "entries" in data, "Response should contain entries"
    assert len(data["entries"]) > 0, "Should have at least one entry"
    assert data["total_entries"] > 0, "Should have positive entry count"

    print(f"✅ Leaderboard has {data['total_entries']} entries, Prize pool: ${data['prize_pool']}")


def test_get_transactions():
    """Test getting transaction history."""
    print("\n🧪 Testing get transactions...")

    headers = {"Authorization": f"Bearer {TestState.access_token}"}
    response = requests.get(f"{API_URL}/transactions", headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "transactions" in data, "Response should contain transactions"
    assert len(data["transactions"]) >= 2, "Should have at least 2 transactions (deposit + contest entry)"

    print(f"✅ User has {len(data['transactions'])} transactions")


def test_unauthorized_access():
    """Test that protected endpoints require authentication."""
    print("\n🧪 Testing unauthorized access protection...")

    # Try to access profile without token
    response = requests.get(f"{API_URL}/auth/profile")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Try to create team without token
    response = requests.post(
        f"{API_URL}/teams", json={"match_id": TestState.match_id, "team_name": "Fail Team", "players": []}
    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    print("✅ Unauthorized access properly blocked")


def run_all_tests():
    """Run all API tests in sequence."""
    print("=" * 60)
    print("🏏 CRICKET FANTASY API TESTS")
    print("=" * 60)

    tests = [
        test_register_user,
        test_login_user,
        test_get_profile,
        test_get_matches,
        test_get_players_for_match,
        test_get_contests,
        test_add_funds_to_wallet,
        test_create_team,
        test_join_contest,
        test_get_wallet_balance,
        test_get_my_contests,
        test_get_leaderboard,
        test_get_transactions,
        test_unauthorized_access,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__} error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)