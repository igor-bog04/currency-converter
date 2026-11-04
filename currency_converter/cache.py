"""JSON cache for persisting the last successful rate snapshot."""
import json
import os
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from currency_converter.models import Currency, RateSnapshot


class RateCache:
    def __init__(self, path: Optional[str] = None):
        if path is not None:
            self.path = path
        else:
            appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
            self.path = os.path.join(appdata, "CurrencyConverter", "cache.json")

    def save(self, snapshot: RateSnapshot) -> None:
        cache_dir = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(cache_dir, exist_ok=True)

        data = {
            "rate_date": snapshot.rate_date.isoformat(),
            "source": snapshot.source,
            "currencies": {
                code: {
                    "code": curr.code,
                    "name": curr.name,
                    "rate_to_mdl": str(curr.rate_to_mdl),
                }
                for code, curr in snapshot.currencies.items()
            },
        }

        temp_path = os.path.join(cache_dir, f".cache_tmp_{uuid.uuid4().hex}")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.path)
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def load(self) -> Optional[RateSnapshot]:
        if not os.path.exists(self.path):
            return None

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)

            rate_date = date.fromisoformat(data["rate_date"])
            source = data.get("source", "BNM")
            currencies_data = data.get("currencies", {})

            currencies = {}
            for code, c_data in currencies_data.items():
                currencies[code] = Currency(
                    code=c_data["code"],
                    name=c_data["name"],
                    rate_to_mdl=Decimal(c_data["rate_to_mdl"]),
                )

            return RateSnapshot(rate_date=rate_date, source=source, currencies=currencies)
        except Exception:
            return None
