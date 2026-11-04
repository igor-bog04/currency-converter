"""Desktop Currency Converter – application entry point."""
from currency_converter.bnm_client import BnmClient
from currency_converter.cache import RateCache
from currency_converter.rate_provider import RateProvider
from currency_converter.ui import CurrencyConverterApp


def main():
    client = BnmClient()
    cache = RateCache()
    provider = RateProvider(client=client, cache=cache)
    app = CurrencyConverterApp(provider=provider)
    app.mainloop()


if __name__ == "__main__":
    main()
