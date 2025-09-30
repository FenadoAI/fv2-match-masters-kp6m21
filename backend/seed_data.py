"""Seed script to populate database with sample cricket fantasy data."""

import asyncio
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from models import (
    Match,
    MatchStatus,
    Player,
    PlayerRole,
    Contest,
    ContestStatus,
)

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")


async def seed_data():
    """Seed the database with sample data."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("Starting database seeding...")

    # Clear existing data
    print("Clearing existing data...")
    await db.matches.delete_many({})
    await db.players.delete_many({})
    await db.contests.delete_many({})

    # Create sample matches
    now = datetime.now(timezone.utc)

    match1 = Match(
        title="India vs Australia - T20 World Cup",
        team1="India",
        team2="Australia",
        start_time=now + timedelta(hours=6),
        status=MatchStatus.UPCOMING,
        venue="Melbourne Cricket Ground",
        match_type="T20",
    )

    match2 = Match(
        title="England vs Pakistan - ODI Series",
        team1="England",
        team2="Pakistan",
        start_time=now + timedelta(days=1),
        status=MatchStatus.UPCOMING,
        venue="Lord's Cricket Ground",
        match_type="ODI",
    )

    match3 = Match(
        title="South Africa vs New Zealand - Test Match",
        team1="South Africa",
        team2="New Zealand",
        start_time=now + timedelta(days=2),
        status=MatchStatus.UPCOMING,
        venue="Newlands Cricket Ground",
        match_type="Test",
    )

    await db.matches.insert_many([match1.model_dump(), match2.model_dump(), match3.model_dump()])
    print(f"✓ Created {3} matches")

    # Create players for Match 1 (India vs Australia)
    india_players = [
        Player(name="Virat Kohli", role=PlayerRole.BATSMAN, team="India", base_price=11.5, match_id=match1.id),
        Player(name="Rohit Sharma", role=PlayerRole.BATSMAN, team="India", base_price=10.5, match_id=match1.id),
        Player(name="KL Rahul", role=PlayerRole.WICKET_KEEPER, team="India", base_price=9.5, match_id=match1.id),
        Player(name="Hardik Pandya", role=PlayerRole.ALL_ROUNDER, team="India", base_price=10.0, match_id=match1.id),
        Player(name="Ravindra Jadeja", role=PlayerRole.ALL_ROUNDER, team="India", base_price=9.0, match_id=match1.id),
        Player(name="Jasprit Bumrah", role=PlayerRole.BOWLER, team="India", base_price=10.5, match_id=match1.id),
        Player(name="Mohammed Shami", role=PlayerRole.BOWLER, team="India", base_price=9.0, match_id=match1.id),
        Player(name="Yuzvendra Chahal", role=PlayerRole.BOWLER, team="India", base_price=8.5, match_id=match1.id),
        Player(name="Shubman Gill", role=PlayerRole.BATSMAN, team="India", base_price=8.0, match_id=match1.id),
        Player(name="Rishabh Pant", role=PlayerRole.WICKET_KEEPER, team="India", base_price=9.5, match_id=match1.id),
        Player(name="Axar Patel", role=PlayerRole.ALL_ROUNDER, team="India", base_price=7.5, match_id=match1.id),
    ]

    australia_players = [
        Player(name="Steve Smith", role=PlayerRole.BATSMAN, team="Australia", base_price=11.0, match_id=match1.id),
        Player(name="David Warner", role=PlayerRole.BATSMAN, team="Australia", base_price=10.5, match_id=match1.id),
        Player(name="Alex Carey", role=PlayerRole.WICKET_KEEPER, team="Australia", base_price=8.5, match_id=match1.id),
        Player(name="Glenn Maxwell", role=PlayerRole.ALL_ROUNDER, team="Australia", base_price=10.0, match_id=match1.id),
        Player(
            name="Mitchell Marsh", role=PlayerRole.ALL_ROUNDER, team="Australia", base_price=9.0, match_id=match1.id
        ),
        Player(name="Pat Cummins", role=PlayerRole.BOWLER, team="Australia", base_price=10.5, match_id=match1.id),
        Player(
            name="Mitchell Starc", role=PlayerRole.BOWLER, team="Australia", base_price=10.0, match_id=match1.id
        ),
        Player(name="Adam Zampa", role=PlayerRole.BOWLER, team="Australia", base_price=8.5, match_id=match1.id),
        Player(
            name="Travis Head", role=PlayerRole.BATSMAN, team="Australia", base_price=9.0, match_id=match1.id
        ),
        Player(
            name="Josh Hazlewood", role=PlayerRole.BOWLER, team="Australia", base_price=9.5, match_id=match1.id
        ),
        Player(name="Marcus Stoinis", role=PlayerRole.ALL_ROUNDER, team="Australia", base_price=8.0, match_id=match1.id),
    ]

    all_match1_players = india_players + australia_players
    await db.players.insert_many([p.model_dump() for p in all_match1_players])
    print(f"✓ Created {len(all_match1_players)} players for Match 1")

    # Create players for Match 2 (England vs Pakistan)
    england_players = [
        Player(name="Joe Root", role=PlayerRole.BATSMAN, team="England", base_price=11.0, match_id=match2.id),
        Player(name="Ben Stokes", role=PlayerRole.ALL_ROUNDER, team="England", base_price=10.5, match_id=match2.id),
        Player(name="Jos Buttler", role=PlayerRole.WICKET_KEEPER, team="England", base_price=10.0, match_id=match2.id),
        Player(name="Jonny Bairstow", role=PlayerRole.BATSMAN, team="England", base_price=9.0, match_id=match2.id),
        Player(name="Moeen Ali", role=PlayerRole.ALL_ROUNDER, team="England", base_price=8.5, match_id=match2.id),
        Player(name="Chris Woakes", role=PlayerRole.BOWLER, team="England", base_price=9.0, match_id=match2.id),
        Player(name="Jofra Archer", role=PlayerRole.BOWLER, team="England", base_price=9.5, match_id=match2.id),
        Player(name="Adil Rashid", role=PlayerRole.BOWLER, team="England", base_price=8.0, match_id=match2.id),
        Player(name="Jason Roy", role=PlayerRole.BATSMAN, team="England", base_price=8.5, match_id=match2.id),
        Player(name="Sam Curran", role=PlayerRole.ALL_ROUNDER, team="England", base_price=9.0, match_id=match2.id),
        Player(name="Mark Wood", role=PlayerRole.BOWLER, team="England", base_price=8.5, match_id=match2.id),
    ]

    pakistan_players = [
        Player(name="Babar Azam", role=PlayerRole.BATSMAN, team="Pakistan", base_price=11.5, match_id=match2.id),
        Player(name="Mohammad Rizwan", role=PlayerRole.WICKET_KEEPER, team="Pakistan", base_price=10.0, match_id=match2.id),
        Player(name="Shaheen Afridi", role=PlayerRole.BOWLER, team="Pakistan", base_price=10.5, match_id=match2.id),
        Player(name="Shadab Khan", role=PlayerRole.ALL_ROUNDER, team="Pakistan", base_price=9.0, match_id=match2.id),
        Player(name="Haris Rauf", role=PlayerRole.BOWLER, team="Pakistan", base_price=9.0, match_id=match2.id),
        Player(name="Fakhar Zaman", role=PlayerRole.BATSMAN, team="Pakistan", base_price=9.0, match_id=match2.id),
        Player(name="Iftikhar Ahmed", role=PlayerRole.ALL_ROUNDER, team="Pakistan", base_price=8.0, match_id=match2.id),
        Player(name="Naseem Shah", role=PlayerRole.BOWLER, team="Pakistan", base_price=8.5, match_id=match2.id),
        Player(name="Mohammad Nawaz", role=PlayerRole.ALL_ROUNDER, team="Pakistan", base_price=7.5, match_id=match2.id),
        Player(name="Hasan Ali", role=PlayerRole.BOWLER, team="Pakistan", base_price=8.0, match_id=match2.id),
        Player(name="Imam-ul-Haq", role=PlayerRole.BATSMAN, team="Pakistan", base_price=8.5, match_id=match2.id),
    ]

    all_match2_players = england_players + pakistan_players
    await db.players.insert_many([p.model_dump() for p in all_match2_players])
    print(f"✓ Created {len(all_match2_players)} players for Match 2")

    # Create contests for Match 1
    contest1 = Contest(
        match_id=match1.id,
        name="Mega Contest",
        entry_fee=50.0,
        max_users=100,
        prize_pool=5000.0,
        status=ContestStatus.OPEN,
        prize_distribution={"1": 2000, "2": 1000, "3": 500, "4-10": 100},
    )

    contest2 = Contest(
        match_id=match1.id,
        name="Small League",
        entry_fee=10.0,
        max_users=20,
        prize_pool=200.0,
        status=ContestStatus.OPEN,
        prize_distribution={"1": 100, "2": 60, "3": 40},
    )

    contest3 = Contest(
        match_id=match1.id,
        name="Practice Contest",
        entry_fee=5.0,
        max_users=50,
        prize_pool=250.0,
        status=ContestStatus.OPEN,
        prize_distribution={"1": 125, "2": 75, "3": 50},
    )

    # Create contests for Match 2
    contest4 = Contest(
        match_id=match2.id,
        name="Grand Prize",
        entry_fee=100.0,
        max_users=50,
        prize_pool=5000.0,
        status=ContestStatus.OPEN,
        prize_distribution={"1": 2500, "2": 1500, "3": 1000},
    )

    contest5 = Contest(
        match_id=match2.id,
        name="Starter League",
        entry_fee=20.0,
        max_users=30,
        prize_pool=600.0,
        status=ContestStatus.OPEN,
        prize_distribution={"1": 300, "2": 180, "3": 120},
    )

    all_contests = [contest1, contest2, contest3, contest4, contest5]
    await db.contests.insert_many([c.model_dump() for c in all_contests])
    print(f"✓ Created {len(all_contests)} contests")

    print("\n✅ Database seeding completed successfully!")
    print("\nSummary:")
    print(f"  - Matches: {await db.matches.count_documents({})}")
    print(f"  - Players: {await db.players.count_documents({})}")
    print(f"  - Contests: {await db.contests.count_documents({})}")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_data())