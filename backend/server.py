"""FastAPI server exposing AI agent endpoints and Cricket Fantasy API."""

import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Request, Header, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from ai_agents.agents import AgentConfig, ChatAgent, SearchAgent
from models import (
    User, UserCreate, UserLogin, UserResponse,
    Match, MatchCreate, MatchStatus,
    Player, PlayerCreate, PlayerRole,
    Contest, ContestCreate, ContestStatus,
    Team, TeamCreate, TeamPlayer,
    ContestEntry, ContestJoinRequest,
    Transaction, TransactionType, TransactionStatus, AddFundsRequest,
    LeaderboardEntry, LeaderboardResponse
)
from auth_utils import hash_password, verify_password, create_access_token, verify_token


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent


class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None


def _ensure_db(request: Request):
    try:
        return request.app.state.db
    except AttributeError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=503, detail="Database not ready") from exc


def _get_agent_cache(request: Request) -> Dict[str, object]:
    if not hasattr(request.app.state, "agent_cache"):
        request.app.state.agent_cache = {}
    return request.app.state.agent_cache


async def _get_or_create_agent(request: Request, agent_type: str):
    cache = _get_agent_cache(request)
    if agent_type in cache:
        return cache[agent_type]

    config: AgentConfig = request.app.state.agent_config

    if agent_type == "search":
        cache[agent_type] = SearchAgent(config)
    elif agent_type == "chat":
        cache[agent_type] = ChatAgent(config)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown agent type '{agent_type}'")

    return cache[agent_type]


def clean_mongo_doc(doc):
    """Remove MongoDB _id field from document."""
    if doc and "_id" in doc:
        doc.pop("_id")
    return doc


def clean_mongo_docs(docs):
    """Remove MongoDB _id field from list of documents."""
    return [clean_mongo_doc(doc) for doc in docs]


async def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> User:
    """Dependency to get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    db = _ensure_db(request)
    user = await db.users.find_one({"id": payload.get("sub")})

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return User(**user)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv(ROOT_DIR / ".env")

    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME")

    if not mongo_url or not db_name:
        missing = [name for name, value in {"MONGO_URL": mongo_url, "DB_NAME": db_name}.items() if not value]
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    client = AsyncIOMotorClient(mongo_url)

    try:
        app.state.mongo_client = client
        app.state.db = client[db_name]
        app.state.agent_config = AgentConfig()
        app.state.agent_cache = {}
        logger.info("AI Agents API starting up")
        yield
    finally:
        client.close()
        logger.info("AI Agents API shutdown complete")


app = FastAPI(
    title="AI Agents API",
    description="Minimal AI Agents API with LangGraph and MCP support",
    lifespan=lifespan,
)

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate, request: Request):
    db = _ensure_db(request)
    status_obj = StatusCheck(**input.model_dump())
    await db.status_checks.insert_one(status_obj.model_dump())
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks(request: Request):
    db = _ensure_db(request)
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(chat_request: ChatRequest, request: Request):
    try:
        agent = await _get_or_create_agent(request, chat_request.agent_type)
        response = await agent.execute(chat_request.message)

        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=chat_request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error in chat endpoint")
        return ChatResponse(
            success=False,
            response="",
            agent_type=chat_request.agent_type,
            capabilities=[],
            error=str(exc),
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(search_request: SearchRequest, request: Request):
    try:
        search_agent = await _get_or_create_agent(request, "search")
        search_prompt = (
            f"Search for information about: {search_request.query}. "
            "Provide a comprehensive summary with key findings."
        )
        result = await search_agent.execute(search_prompt, use_tools=True)

        if result.success:
            metadata = result.metadata or {}
            return SearchResponse(
                success=True,
                query=search_request.query,
                summary=result.content,
                search_results=metadata,
                sources_count=int(metadata.get("tool_run_count", metadata.get("tools_used", 0)) or 0),
            )

        return SearchResponse(
            success=False,
            query=search_request.query,
            summary="",
            sources_count=0,
            error=result.error,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error in search endpoint")
        return SearchResponse(
            success=False,
            query=search_request.query,
            summary="",
            sources_count=0,
            error=str(exc),
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities(request: Request):
    try:
        search_agent = await _get_or_create_agent(request, "search")
        chat_agent = await _get_or_create_agent(request, "chat")

        return {
            "success": True,
            "capabilities": {
                "search_agent": search_agent.get_capabilities(),
                "chat_agent": chat_agent.get_capabilities(),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error getting capabilities")
        return {"success": False, "error": str(exc)}


# ============================
# Cricket Fantasy API Routes
# ============================

# Authentication Routes
@api_router.post("/auth/register")
async def register_user(user_data: UserCreate, request: Request):
    """Register a new user."""
    db = _ensure_db(request)

    # Check if username or email already exists
    existing_user = await db.users.find_one({"$or": [{"username": user_data.username}, {"email": user_data.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Create new user
    hashed_pwd = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pwd,
    )

    await db.users.insert_one(user.model_dump())

    # Create access token
    access_token = create_access_token({"sub": user.id, "username": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.model_dump()),
    }


@api_router.post("/auth/login")
async def login_user(credentials: UserLogin, request: Request):
    """Login a user."""
    db = _ensure_db(request)

    # Find user
    user_data = await db.users.find_one({"username": credentials.username})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = User(**user_data)

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create access token
    access_token = create_access_token({"sub": user.id, "username": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.model_dump()),
    }


@api_router.get("/auth/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(**current_user.model_dump())


# Match Routes
@api_router.get("/matches")
async def get_matches(request: Request, status: Optional[str] = None):
    """Get all matches, optionally filtered by status."""
    db = _ensure_db(request)

    query = {}
    if status:
        query["status"] = status

    matches = await db.matches.find(query).sort("start_time", 1).to_list(100)
    return {"matches": clean_mongo_docs(matches)}


@api_router.get("/matches/{match_id}")
async def get_match(match_id: str, request: Request):
    """Get a specific match by ID."""
    db = _ensure_db(request)

    match = await db.matches.find_one({"id": match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return clean_mongo_doc(match)


@api_router.post("/matches", response_model=Match)
async def create_match(match_data: MatchCreate, request: Request, current_user: User = Depends(get_current_user)):
    """Create a new match (admin only for now)."""
    db = _ensure_db(request)

    match = Match(**match_data.model_dump())
    await db.matches.insert_one(match.model_dump())

    return match


# Player Routes
@api_router.get("/players/{match_id}")
async def get_players_for_match(match_id: str, request: Request):
    """Get all players available for a specific match."""
    db = _ensure_db(request)

    # Verify match exists
    match = await db.matches.find_one({"id": match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    players = await db.players.find({"match_id": match_id}).to_list(100)
    return {"players": clean_mongo_docs(players)}


@api_router.post("/players", response_model=Player)
async def create_player(player_data: PlayerCreate, request: Request, current_user: User = Depends(get_current_user)):
    """Create a new player (admin only for now)."""
    db = _ensure_db(request)

    player = Player(**player_data.model_dump())
    await db.players.insert_one(player.model_dump())

    return player


# Contest Routes
@api_router.get("/contests")
async def get_contests(request: Request, match_id: Optional[str] = None, status: Optional[str] = None):
    """Get all contests, optionally filtered by match_id and status."""
    db = _ensure_db(request)

    query = {}
    if match_id:
        query["match_id"] = match_id
    if status:
        query["status"] = status

    contests = await db.contests.find(query).to_list(100)
    return {"contests": clean_mongo_docs(contests)}


@api_router.get("/contests/{contest_id}")
async def get_contest(contest_id: str, request: Request):
    """Get a specific contest by ID."""
    db = _ensure_db(request)

    contest = await db.contests.find_one({"id": contest_id})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    return clean_mongo_doc(contest)


@api_router.post("/contests", response_model=Contest)
async def create_contest(contest_data: ContestCreate, request: Request, current_user: User = Depends(get_current_user)):
    """Create a new contest (admin only for now)."""
    db = _ensure_db(request)

    # Verify match exists
    match = await db.matches.find_one({"id": contest_data.match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Calculate prize pool from entry fee and max users
    prize_pool = contest_data.entry_fee * contest_data.max_users

    contest = Contest(
        **contest_data.model_dump(),
        prize_pool=prize_pool,
    )
    await db.contests.insert_one(contest.model_dump())

    return contest


@api_router.post("/contests/{contest_id}/join")
async def join_contest(
    contest_id: str, join_request: ContestJoinRequest, request: Request, current_user: User = Depends(get_current_user)
):
    """Join a contest with a team."""
    db = _ensure_db(request)

    # Get contest
    contest_data = await db.contests.find_one({"id": contest_id})
    if not contest_data:
        raise HTTPException(status_code=404, detail="Contest not found")

    contest = Contest(**contest_data)

    # Check if contest is open
    if contest.status != ContestStatus.OPEN:
        raise HTTPException(status_code=400, detail="Contest is not open for joining")

    # Check if contest is full
    if contest.joined_users >= contest.max_users:
        raise HTTPException(status_code=400, detail="Contest is full")

    # Check if user already joined
    existing_entry = await db.contest_entries.find_one({"contest_id": contest_id, "user_id": current_user.id})
    if existing_entry:
        raise HTTPException(status_code=400, detail="You have already joined this contest")

    # Verify team exists and belongs to user
    team_data = await db.teams.find_one({"id": join_request.team_id, "user_id": current_user.id})
    if not team_data:
        raise HTTPException(status_code=404, detail="Team not found or does not belong to you")

    team = Team(**team_data)

    # Verify team is for the same match
    if team.match_id != contest.match_id:
        raise HTTPException(status_code=400, detail="Team is not for this match")

    # Check wallet balance
    if current_user.wallet_balance < contest.entry_fee:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    # Deduct entry fee from wallet
    await db.users.update_one({"id": current_user.id}, {"$inc": {"wallet_balance": -contest.entry_fee}})

    # Create transaction record
    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.CONTEST_ENTRY,
        amount=contest.entry_fee,
        status=TransactionStatus.COMPLETED,
        reference_id=contest_id,
        description=f"Entry fee for contest: {contest.name}",
    )
    await db.transactions.insert_one(transaction.model_dump())

    # Create contest entry
    entry = ContestEntry(contest_id=contest_id, user_id=current_user.id, team_id=join_request.team_id)
    await db.contest_entries.insert_one(entry.model_dump())

    # Update contest joined_users count
    new_joined_count = contest.joined_users + 1
    update_data = {"joined_users": new_joined_count}

    # If contest is now full, mark it as full
    if new_joined_count >= contest.max_users:
        update_data["status"] = ContestStatus.FULL

    await db.contests.update_one({"id": contest_id}, {"$set": update_data})

    return {"success": True, "message": "Successfully joined contest", "entry": entry.model_dump()}


# Team Routes
@api_router.post("/teams", response_model=Team)
async def create_team(team_data: TeamCreate, request: Request, current_user: User = Depends(get_current_user)):
    """Create a fantasy team."""
    db = _ensure_db(request)

    # Verify match exists
    match = await db.matches.find_one({"id": team_data.match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Verify all players exist and belong to the match
    player_ids = [p.player_id for p in team_data.players]
    players = await db.players.find({"id": {"$in": player_ids}, "match_id": team_data.match_id}).to_list(100)

    if len(players) != 11:
        raise HTTPException(status_code=400, detail="Some players are invalid or do not belong to this match")

    # Validate budget (100 credits total)
    total_credits = sum(p["base_price"] for p in players)
    if total_credits > 100:
        raise HTTPException(status_code=400, detail=f"Team exceeds budget. Total: {total_credits}, Max: 100")

    # Validate team composition (minimum requirements)
    role_counts = {}
    for player in players:
        role = player["role"]
        role_counts[role] = role_counts.get(role, 0) + 1

    # Minimum 1 wicket keeper, 3 batsmen, 1 bowler, 1 all-rounder
    if role_counts.get(PlayerRole.WICKET_KEEPER, 0) < 1:
        raise HTTPException(status_code=400, detail="Team must have at least 1 wicket keeper")
    if role_counts.get(PlayerRole.BATSMAN, 0) < 3:
        raise HTTPException(status_code=400, detail="Team must have at least 3 batsmen")
    if role_counts.get(PlayerRole.BOWLER, 0) < 1:
        raise HTTPException(status_code=400, detail="Team must have at least 1 bowler")
    if role_counts.get(PlayerRole.ALL_ROUNDER, 0) < 1:
        raise HTTPException(status_code=400, detail="Team must have at least 1 all-rounder")

    # Create team
    team = Team(user_id=current_user.id, **team_data.model_dump())
    await db.teams.insert_one(team.model_dump())

    return team


@api_router.get("/teams/{team_id}")
async def get_team(team_id: str, request: Request):
    """Get a specific team by ID."""
    db = _ensure_db(request)

    team = await db.teams.find_one({"id": team_id})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return clean_mongo_doc(team)


@api_router.get("/teams/user/{user_id}")
async def get_user_teams(user_id: str, request: Request):
    """Get all teams for a user."""
    db = _ensure_db(request)

    teams = await db.teams.find({"user_id": user_id}).to_list(100)
    return {"teams": clean_mongo_docs(teams)}


@api_router.get("/my-teams")
async def get_my_teams(request: Request, current_user: User = Depends(get_current_user)):
    """Get current user's teams."""
    db = _ensure_db(request)

    teams = await db.teams.find({"user_id": current_user.id}).to_list(100)
    return {"teams": clean_mongo_docs(teams)}


# Wallet & Payment Routes
@api_router.get("/wallet/balance")
async def get_wallet_balance(current_user: User = Depends(get_current_user)):
    """Get current user's wallet balance."""
    return {"balance": current_user.wallet_balance}


@api_router.post("/wallet/add-funds")
async def add_funds(funds_request: AddFundsRequest, request: Request, current_user: User = Depends(get_current_user)):
    """Add funds to wallet via Stripe (placeholder - needs Stripe integration)."""
    db = _ensure_db(request)

    # TODO: Integrate with Stripe to process actual payment
    # For now, we'll simulate successful payment
    # In production, you would:
    # 1. Create a payment intent with Stripe
    # 2. Confirm the payment
    # 3. Only credit wallet if payment succeeds

    # Simulate Stripe payment (this is a placeholder)
    payment_successful = True
    stripe_payment_id = f"stripe_sim_{uuid.uuid4()}"

    if not payment_successful:
        raise HTTPException(status_code=400, detail="Payment failed")

    # Credit wallet
    await db.users.update_one({"id": current_user.id}, {"$inc": {"wallet_balance": funds_request.amount}})

    # Create transaction record
    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.DEPOSIT,
        amount=funds_request.amount,
        status=TransactionStatus.COMPLETED,
        reference_id=stripe_payment_id,
        description="Wallet deposit via Stripe",
    )
    await db.transactions.insert_one(transaction.model_dump())

    # Get updated balance
    updated_user = await db.users.find_one({"id": current_user.id})

    return {
        "success": True,
        "message": "Funds added successfully",
        "new_balance": updated_user["wallet_balance"],
        "transaction_id": transaction.id,
    }


@api_router.get("/transactions")
async def get_transactions(request: Request, current_user: User = Depends(get_current_user)):
    """Get user's transaction history."""
    db = _ensure_db(request)

    transactions = await db.transactions.find({"user_id": current_user.id}).sort("created_at", -1).to_list(100)
    return {"transactions": clean_mongo_docs(transactions)}


# Leaderboard Routes
@api_router.get("/contests/{contest_id}/leaderboard", response_model=LeaderboardResponse)
async def get_contest_leaderboard(contest_id: str, request: Request):
    """Get leaderboard for a contest."""
    db = _ensure_db(request)

    # Get contest
    contest_data = await db.contests.find_one({"id": contest_id})
    if not contest_data:
        raise HTTPException(status_code=404, detail="Contest not found")

    contest = Contest(**contest_data)

    # Get all entries for this contest
    entries = await db.contest_entries.find({"contest_id": contest_id}).to_list(1000)

    # Build leaderboard entries with team details
    leaderboard_entries = []
    for entry in entries:
        team_data = await db.teams.find_one({"id": entry["team_id"]})
        user_data = await db.users.find_one({"id": entry["user_id"]})

        if team_data and user_data:
            leaderboard_entries.append(
                {
                    "user_id": user_data["id"],
                    "username": user_data["username"],
                    "team_id": team_data["id"],
                    "team_name": team_data["team_name"],
                    "total_points": team_data.get("total_points", 0),
                    "winnings": entry.get("winnings", 0),
                }
            )

    # Sort by total points (descending)
    leaderboard_entries.sort(key=lambda x: x["total_points"], reverse=True)

    # Assign ranks
    for idx, entry in enumerate(leaderboard_entries, start=1):
        entry["rank"] = idx

    return LeaderboardResponse(
        contest_id=contest_id,
        match_id=contest.match_id,
        entries=[LeaderboardEntry(**e) for e in leaderboard_entries],
        total_entries=len(leaderboard_entries),
        prize_pool=contest.prize_pool,
    )


# My Contests Route
@api_router.get("/my-contests")
async def get_my_contests(request: Request, current_user: User = Depends(get_current_user)):
    """Get contests the current user has joined."""
    db = _ensure_db(request)

    # Get user's contest entries
    entries = await db.contest_entries.find({"user_id": current_user.id}).to_list(100)

    contest_ids = [entry["contest_id"] for entry in entries]

    # Get contest details
    contests = await db.contests.find({"id": {"$in": contest_ids}}).to_list(100)

    # Enrich with match and team details
    result = []
    for contest in contests:
        match = await db.matches.find_one({"id": contest["match_id"]})
        entry = next((e for e in entries if e["contest_id"] == contest["id"]), None)

        team = None
        if entry:
            team = await db.teams.find_one({"id": entry["team_id"]})

        result.append({
            "contest": clean_mongo_doc(contest),
            "match": clean_mongo_doc(match),
            "entry": clean_mongo_doc(entry),
            "team": clean_mongo_doc(team)
        })

    return {"my_contests": result}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
