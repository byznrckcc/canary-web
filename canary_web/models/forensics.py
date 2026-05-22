import hashlib
import ipaddress
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Integer,
    String, Text, create_engine
)
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

class ThreatLevel(PyEnum):
    LOW      = "Low"
    MEDIUM   = "Medium"
    HIGH     = "High"
    CRITICAL = "Critical"

DATACENTER_CIDR_RANGES: list[str] = [
    "3.0.0.0/8", "13.32.0.0/15", "52.0.0.0/6",
    "13.64.0.0/11", "20.0.0.0/8", "40.64.0.0/10",
    "34.0.0.0/8", "35.186.0.0/17",
    "104.16.0.0/13", "172.64.0.0/13",
    "159.65.0.0/16", "167.98.0.0/16",
    "45.33.0.0/17", "139.162.0.0/16",
    "95.216.0.0/16", "116.203.0.0/16",
    "51.68.0.0/16", "54.36.0.0/14",
]

_COMPILED_RANGES = None

def _get_compiled_ranges():
    global _COMPILED_RANGES
    if _COMPILED_RANGES is None:
        _COMPILED_RANGES = [
            ipaddress.ip_network(cidr, strict=False)
            for cidr in DATACENTER_CIDR_RANGES
        ]
    return _COMPILED_RANGES

def is_datacenter_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    if addr.is_private or addr.is_loopback or addr.is_link_local:
        return False
    return any(addr in network for network in _get_compiled_ranges())

def generate_browser_fingerprint(user_agent: str, ip: str, extra: str = "") -> str:
    raw = f"{user_agent}|{ip}|{extra}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class CanaryHit(Base):
    __tablename__ = "canary_hits"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    token_id   = Column(String(64),  nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    ip_address  = Column(String(45),  nullable=True)
    user_agent  = Column(Text,        nullable=True)
    referer     = Column(Text,        nullable=True)
    http_method = Column(String(10),  nullable=True)
    country     = Column(String(2),   nullable=True)
    asn         = Column(String(20),  nullable=True)
    browser_fingerprint = Column(String(128), nullable=True, index=True)
    screen_resolution = Column(String(16), nullable=True)
    system_languages = Column(String(128), nullable=True)
    is_vpn_or_tor = Column(Boolean, nullable=False, default=False, index=True)
    threat_level = Column(Enum(ThreatLevel, name="threat_level_enum"), nullable=False, default=ThreatLevel.LOW, index=True)
    notes = Column(Text, nullable=True)

    def populate_datacenter_flag(self) -> None:
        if self.ip_address:
            self.is_vpn_or_tor = is_datacenter_ip(self.ip_address)

    def set_fingerprint(self, user_agent: str = "", extra: str = "") -> None:
        self.browser_fingerprint = generate_browser_fingerprint(
            user_agent or (self.user_agent or ""),
            self.ip_address or "",
            extra,
        )
