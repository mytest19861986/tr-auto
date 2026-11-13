"""Read-only Alpaca Paper account check; fixed broker host, no order methods."""

from __future__ import annotations

import getpass
import json
import os
from dataclasses import dataclass
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


_PAPER_ACCOUNT_URL = "https://paper-api.alpaca.markets/v2/account"


class PaperConnectionError(RuntimeError):
    """Paper account could not be verified without revealing broker responses."""


@dataclass(frozen=True)
class PaperAccountStatus:
    status: str
    account_blocked: bool
    trading_blocked: bool
    shorting_enabled: bool


def inspect_paper_account(
    api_key_id: str,
    api_secret_key: str,
    *,
    opener: Callable = urlopen,
) -> PaperAccountStatus:
    """GET one paper-only endpoint; never returns account IDs, balances or keys.

    The opener exists solely for injecting a safe offline test stub. The URL
    cannot be overridden by configuration or caller.
    """
    if not api_key_id or not api_key_id.strip() or not api_secret_key or not api_secret_key.strip():
        raise PaperConnectionError("Missing paper credentials; enter them locally.")

    request = Request(
        _PAPER_ACCOUNT_URL,
        data=None,
        headers={
            "APCA-API-KEY-ID": api_key_id,
            "APCA-API-SECRET-KEY": api_secret_key,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with opener(request, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise PaperConnectionError(f"Paper API responded with HTTP {exc.code}.") from None
    except (URLError, OSError, TimeoutError) as exc:
        raise PaperConnectionError("Could not reach the paper API endpoint.") from None
    except (ValueError, TypeError):
        raise PaperConnectionError("Paper API returned invalid JSON.") from None

    if not isinstance(payload, dict) or not isinstance(payload.get("status"), str):
        raise PaperConnectionError("Paper API response lacks account status.")
    return PaperAccountStatus(
        status=payload["status"],
        account_blocked=payload.get("account_blocked") is True,
        trading_blocked=payload.get("trading_blocked") is True,
        shorting_enabled=payload.get("shorting_enabled") is True,
    )


def main() -> int:
    print("TR-AUTO | Alpaca PAPER account | read-only check")
    print("No credentials will be saved and no orders will be submitted.")
    key_id = os.getenv("ALPACA_PAPER_KEY_ID") or getpass.getpass("Paper key ID (hidden): ")
    secret = os.getenv("ALPACA_PAPER_SECRET_KEY") or getpass.getpass("Paper secret (hidden): ")
    try:
        result = inspect_paper_account(key_id, secret)
    except PaperConnectionError as exc:
        print(f"PAPER_CONNECTION_UNVERIFIED: {exc}")
        return 1
    print("PAPER_API_CONNECTED: yes")
    print(f"Account status: {result.status}")
    print(f"Account blocked: {result.account_blocked}")
    print(f"Trading blocked: {result.trading_blocked}")
    print(f"Shorting enabled (account capability): {result.shorting_enabled}")
    print("Note: account capability alone does not verify stock borrow eligibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
