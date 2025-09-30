"""Database models for Cricket Fantasy Sports App."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class MatchStatus(str, Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ContestStatus(str, Enum):
    OPEN = "open"
    FULL = "full"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PlayerRole(str, Enum):
    BATSMAN = "batsman"
    BOWLER = "bowler"
    ALL_ROUNDER = "all_rounder"
    WICKET_KEEPER = "wicket_keeper"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    CONTEST_ENTRY = "contest_entry"
    CONTEST_REFUND = "contest_refund"
    WINNING = "winning"
    WITHDRAWAL = "withdrawal"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    password_hash: str
    wallet_balance: float = 0.0
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    wallet_balance: float
    role: UserRole
    created_at: datetime


# Match Models
class Match(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    team1: str
    team2: str
    start_time: datetime
    status: MatchStatus = MatchStatus.UPCOMING
    venue: str
    match_type: str  # T20, ODI, Test
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MatchCreate(BaseModel):
    title: str
    team1: str
    team2: str
    start_time: datetime
    venue: str
    match_type: str


# Player Models
class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: PlayerRole
    team: str  # team1 or team2
    base_price: float  # credits (1-15)
    current_points: float = 0.0
    match_id: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlayerCreate(BaseModel):
    name: str
    role: PlayerRole
    team: str
    base_price: float
    match_id: str
    image_url: Optional[str] = None


# Contest Models
class Contest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str
    name: str
    entry_fee: float
    prize_pool: float
    max_users: int
    joined_users: int = 0
    status: ContestStatus = ContestStatus.OPEN
    prize_distribution: dict = Field(default_factory=dict)  # {rank: prize_amount}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContestCreate(BaseModel):
    match_id: str
    name: str
    entry_fee: float
    max_users: int
    prize_distribution: dict


# Team Models
class TeamPlayer(BaseModel):
    player_id: str
    is_captain: bool = False
    is_vice_captain: bool = False


class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    match_id: str
    team_name: str
    players: List[TeamPlayer]  # 11 players
    total_points: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TeamCreate(BaseModel):
    match_id: str
    team_name: str
    players: List[TeamPlayer]

    @field_validator("players")
    @classmethod
    def validate_players(cls, v):
        if len(v) != 11:
            raise ValueError("Team must have exactly 11 players")

        captain_count = sum(1 for p in v if p.is_captain)
        vice_captain_count = sum(1 for p in v if p.is_vice_captain)

        if captain_count != 1:
            raise ValueError("Team must have exactly 1 captain")
        if vice_captain_count != 1:
            raise ValueError("Team must have exactly 1 vice captain")

        return v


# Contest Entry Models
class ContestEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contest_id: str
    user_id: str
    team_id: str
    rank: Optional[int] = None
    winnings: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContestJoinRequest(BaseModel):
    contest_id: str
    team_id: str


# Transaction Models
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: TransactionType
    amount: float
    status: TransactionStatus = TransactionStatus.PENDING
    reference_id: Optional[str] = None  # payment gateway reference
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AddFundsRequest(BaseModel):
    amount: float
    payment_method_id: str  # Stripe payment method ID

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v < 10:
            raise ValueError("Minimum deposit amount is 10")
        if v > 10000:
            raise ValueError("Maximum deposit amount is 10000")
        return v


# Leaderboard Models
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    username: str
    team_id: str
    team_name: str
    total_points: float
    winnings: float = 0.0


class LeaderboardResponse(BaseModel):
    contest_id: str
    match_id: str
    entries: List[LeaderboardEntry]
    total_entries: int
    prize_pool: float