"""Authentication models for the NEP API."""

from __future__ import annotations

from typing import Any


class UserInfo:
    """User information returned after sign-in."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def uid(self) -> str:
        return self.raw_data["uid"]

    @property
    def email(self) -> str:
        return self.raw_data["email"]

    @property
    def country(self) -> str:
        return self.raw_data.get("country", "")

    @property
    def state(self) -> str:
        return self.raw_data.get("state", "")

    @property
    def role(self) -> int:
        return self.raw_data.get("role", 0)

    @property
    def group_id(self) -> int:
        return self.raw_data.get("groupId", 0)

    @property
    def group_name(self) -> str:
        return self.raw_data.get("groupName", "")

    @property
    def header_img(self) -> str:
        return self.raw_data.get("headerImg", "")

    @property
    def default_area(self) -> str:
        return self.raw_data.get("defaultArea", "")

    @property
    def company_id(self) -> int:
        return self.raw_data.get("companyId", 0)

    @property
    def is_company_owner(self) -> int:
        return self.raw_data.get("isCompanyOwner", 0)

    @property
    def oem_id(self) -> int:
        return self.raw_data.get("oemid", 0)

    @property
    def oem_web(self) -> str:
        return self.raw_data.get("oemweb", "")


class TokenInfo:
    """JWT token information."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def token(self) -> str:
        return self.raw_data["token"]

    @property
    def expires_at(self) -> int:
        return self.raw_data["expiresAt"]

    @property
    def duration(self) -> int:
        return self.raw_data.get("duration", 43200)


class AuthData:
    """Combined authentication data from sign-in."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def user_info(self) -> UserInfo:
        return UserInfo(self.raw_data["userInfo"])

    @property
    def token_info(self) -> TokenInfo:
        return TokenInfo(self.raw_data["tokenInfo"])

    @property
    def site_count(self) -> int:
        return self.raw_data.get("siteCount", 0)


class AccountInfo:
    """Detailed user account information from /account/info."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def uid(self) -> str:
        return self.raw_data.get("uid", "")

    @property
    def email(self) -> str:
        return self.raw_data.get("email", "")

    @property
    def user_type(self) -> int:
        return self.raw_data.get("userType", 0)

    @property
    def country_name(self) -> str:
        return self.raw_data.get("countryName", "")

    @property
    def state_name(self) -> str:
        return self.raw_data.get("stateName", "")

    @property
    def country_code(self) -> str:
        return self.raw_data.get("countryCode", "")

    @property
    def state_code(self) -> str:
        return self.raw_data.get("StateCode", "")

    @property
    def city(self) -> str:
        return self.raw_data.get("city", "")

    @property
    def street(self) -> str:
        return self.raw_data.get("street", "")

    @property
    def contact_person(self) -> str:
        return self.raw_data.get("contactPerson", "")

    @property
    def contact_number(self) -> str:
        return self.raw_data.get("contactNumber", "")

    @property
    def header_img(self) -> str:
        return self.raw_data.get("headerImg", "")

    @property
    def full_header_img(self) -> str:
        return self.raw_data.get("fullHeaderImg", "")

    @property
    def is_auth(self) -> bool:
        return self.raw_data.get("is_auth", False)

    @property
    def group_id(self) -> int:
        return self.raw_data.get("groupId", 0)

    @property
    def group_name(self) -> str:
        return self.raw_data.get("groupName", "")

    @property
    def parent_id(self) -> str:
        return self.raw_data.get("parent_id", "")

    @property
    def parent_email(self) -> str:
        return self.raw_data.get("parent_email", "")

    @property
    def company_id(self) -> int:
        return self.raw_data.get("company_id", 0)

    @property
    def oem_id(self) -> int:
        return self.raw_data.get("oemid", 0)

    @property
    def oem_web(self) -> str:
        return self.raw_data.get("oemweb", "")

    @property
    def is_company_owner(self) -> int:
        return self.raw_data.get("isCompanyOwner", 0)

    @property
    def is_black(self) -> int:
        return self.raw_data.get("isBlack", 0)