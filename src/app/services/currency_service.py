"""Valyuta konversiyasi yordamchi servisi: USD/UZS o'rtasida sana bo'yicha kurs orqali o'tkazish."""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import Currency
from app.core.exceptions import AppError
from app.repositories.exchange_rate_repository import ExchangeRateRepository


class CurrencyConversionError(AppError):
    def __init__(self, rate_date: date) -> None:
        self.rate_date = rate_date
        super().__init__(f"{rate_date} sanasi uchun kurs topilmadi")


class CurrencyService:
    def __init__(self, session: Session) -> None:
        self._repo = ExchangeRateRepository(session)

    def to_uzs(self, amount: Decimal, currency: Currency, on_date: date) -> Decimal:
        """Istalgan valyutadagi summani UZS ga o'tkazadi.

        UZS → UZS: o'zgarmaydi. USD → UZS: sanaga eng yaqin (yoki teng) kurs bilan
        ko'paytiradi. Kurs topilmasa: `CurrencyConversionError`.
        """
        if currency == Currency.UZS:
            return amount
        rate = self._repo.get_latest_on_or_before(on_date)
        if rate is None:
            raise CurrencyConversionError(on_date)
        return (amount * rate.usd_to_uzs).quantize(Decimal("0.01"))

    def to_usd(self, amount: Decimal, currency: Currency, on_date: date) -> Decimal:
        """UZS ni USD ga o'tkazadi. USD → USD: o'zgarmaydi."""
        if currency == Currency.USD:
            return amount
        rate = self._repo.get_latest_on_or_before(on_date)
        if rate is None:
            raise CurrencyConversionError(on_date)
        return (amount / rate.usd_to_uzs).quantize(Decimal("0.0001"))

    def convert(
        self, amount: Decimal, from_currency: Currency, to_currency: Currency, on_date: date
    ) -> Decimal:
        """Ixtiyoriy ikki valyuta orasida o'tkazadi (FIFO/Financial Summary uchun umumiy yo'l)."""
        if from_currency == to_currency:
            return amount
        if to_currency == Currency.UZS:
            return self.to_uzs(amount, from_currency, on_date)
        return self.to_usd(amount, from_currency, on_date)
