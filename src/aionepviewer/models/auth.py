"""Authentication models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class UserInfo:
    """User information returned after sign-in."""

    uid: str
    email: str
    country: str
    state: str
    role: int
    group_id: int
    group_name: str
    header_img: str
    default_area: str
    company_id: int
    is_company_owner: int
    oem_id: int
    oem_web: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UserInfo:
        return cls(
            uid=data["uid"],
            email=data["email"],
            country=data.get("country", ""),
            state=data.get("state", ""),
            role=data.get("role", 0),
            group_id=data.get("groupId", 0),
            group_name=data.get("groupName", ""),
            header_img=data.get("headerImg", ""),
            default_area=data.get("defaultArea", ""),
            company_id=data.get("companyId", 0),
            is_company_owner=data.get("isCompanyOwner", 0),
            oem_id=data.get("oemid", 0),
            oem_web=data.get("oemweb", ""),
        )


@dataclass(slots=True)
class TokenInfo:
    """JWT token information."""

    token: str
    expires_at: int
    duration: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TokenInfo:
        return cls(
            token=data["token"],
            expires_at=data["expiresAt"],
            duration=data.get("duration", 43200),
        )


@dataclass(slots=True)
class AuthData:
    """Combined authentication data from sign-in."""

    user_info: UserInfo
    token_info: TokenInfo
    site_count: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AuthData:
        return cls(
            user_info=UserInfo.from_api(data["userInfo"]),
            token_info=TokenInfo.from_api(data["tokenInfo"]),
            site_count=data.get("siteCount", 0),
        )


@dataclass(slots=True)
class AccountInfo:
    """Detailed user account information from /account/info."""

    uid: str
    email: str
    user_type: int
    country_name: str
    state_name: str
    country_code: str
    state_code: str
    city: str
    street: str
    contact_person: str
    contact_number: str
    header_img: str
    full_header_img: str
    is_auth: bool
    group_id: int
    group_name: str
    parent_id: str
    parent_email: str
    company_id: int
    oem_id: int
    oem_web: str
    is_company_owner: int
    is_black: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AccountInfo:
        return cls(
            uid=data.get("uid", ""),
            email=data.get("email", ""),
            user_type=data.get("userType", 0),
            country_name=data.get("countryName", ""),
            state_name=data.get("stateName", ""),
            country_code=data.get("countryCode", ""),
            state_code=data.get("StateCode", ""),
            city=data.get("city", ""),
            street=data.get("street", ""),
            contact_person=data.get("contactPerson", ""),
            contact_number=data.get("contactNumber", ""),
            header_img=data.get("headerImg", ""),
            full_header_img=data.get("fullHeaderImg", ""),
            is_auth=data.get("is_auth", False),
            group_id=data.get("groupId", 0),
            group_name=data.get("groupName", ""),
            parent_id=data.get("parent_id", ""),
            parent_email=data.get("parent_email", ""),
            company_id=data.get("company_id", 0),
            oem_id=data.get("oemid", 0),
            oem_web=data.get("oemweb", ""),
            is_company_owner=data.get("isCompanyOwner", 0),
            is_black=data.get("isBlack", 0),
        )