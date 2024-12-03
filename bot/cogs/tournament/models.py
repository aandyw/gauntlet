from dataclasses import dataclass


@dataclass
class Voter:
    name: str


@dataclass
class Candidate:
    name: str
    elo: float


@dataclass
class Tournament:
    name: str
    candidates: list[Candidate]
    voters: list[Voter]
