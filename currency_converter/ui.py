"""CustomTkinter UI for the currency converter application."""
from datetime import date, datetime
from decimal import Decimal
import threading
from typing import Optional, Dict
import customtkinter

from currency_converter.converter import convert
from currency_converter.interfaces import NoRatesForDateError, SourceUnavailableError
from currency_converter.models import ConversionResult, RateSnapshot
from currency_converter.validation import validate_amount, AmountValidationError

# Design System Colors
ACCENT_COLOR = ("#4F46E5", "#6366F1")       # Indigo: light / dark
ACCENT_HOVER = ("#4338CA", "#4F46E5")
CARD_BG = ("#FFFFFF", "#1E293B")            # White / Slate-800
CARD_BORDER = ("#E2E8F0", "#334155")
WINDOW_BG = ("#F8FAFC", "#0F172A")          # Slate-50 / Slate-900
DISABLED_BG = ("#E2E8F0", "#334155")
DISABLED_TEXT = ("#94A3B8", "#64748B")
TEXT_PRIMARY = ("#0F172A", "#F8FAFC")
TEXT_MUTED = ("#64748B", "#94A3B8")
TEXT_SUBTLE = ("#94A3B8", "#64748B")


def can_convert(amount: str, source: Optional[str], target: Optional[str]) -> bool:
    if not source or not target:
        return False
    try:
        validate_amount(amount)
        return True
    except AmountValidationError:
        return False


def format_fallback_message(requested: date, effective: date) -> str:
    req_str = requested.strftime("%d.%m.%Y")
    eff_str = effective.strftime("%d.%m.%Y")
    return f"Курсы на {req_str} не опубликованы. Используются официальные курсы за {eff_str}."


def format_error_message(error_type: str, **kwargs) -> str:
    if error_type == "no_network":
        return "Отсутствует подключение к сети. Не удалось получить официальные курсы BNM."
    elif error_type == "cache_available":
        cache_date = kwargs.get("cache_date")
        date_str = cache_date.strftime("%d.%m.%Y") if cache_date else "неизвестную дату"
        return f"Источник BNM недоступен. Доступны сохраненные курсы за {date_str}. Использовать их?"
    elif error_type == "no_cache":
        return "Официальные курсы BNM недоступны, сохраненные локальные данные отсутствуют."
    elif error_type == "timeout":
        return "Превышено время ожидания ответа от сервера BNM (10 секунд)."
    elif error_type == "malformed_xml":
        return "Получен некорректный ответ (XML) от сервера BNM."
    else:
        return "Произошла ошибка при получении курсов валют."


def format_result(result: ConversionResult, source_code: str, target_code: str) -> str:
    date_str = result.snapshot_date.strftime("%d.%m.%Y")
    return (
        f"{result.converted_amount} {target_code}\n"
        f"1 {source_code} = {result.source_to_target_rate} {target_code}  |  "
        f"1 {target_code} = {result.target_to_source_rate} {source_code}\n"
        f"Дата курса: {date_str}  |  Источник: {result.source}"
    )


class CurrencyConverterApp(customtkinter.CTk):
    def __init__(self, provider=None):
        super().__init__()

        self.provider = provider
        self.title("Конвертер валют BNM")
        self.geometry("660x780")
        self.minsize(600, 740)

        customtkinter.set_appearance_mode("dark")
        self.configure(fg_color=WINDOW_BG)

        self.current_snapshot: Optional[RateSnapshot] = None
        self.pending_cache_snapshot: Optional[RateSnapshot] = None
        self.is_fetching = False

        self._setup_ui()
        self._set_initial_date()

        if self.provider is not None:
            self.fetch_rates_for_current_date()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # 1. Header Card
        header_card = customtkinter.CTkFrame(
            self,
            corner_radius=14,
            fg_color=CARD_BG,
            border_width=1,
            border_color=CARD_BORDER,
        )
        header_card.grid(row=0, column=0, padx=20, pady=(20, 16), sticky="ew")
        header_card.grid_columnconfigure(0, weight=1)

        title_label = customtkinter.CTkLabel(
            header_card,
            text="Конвертер валют BNM",
            font=customtkinter.CTkFont(size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        title_label.grid(row=0, column=0, padx=20, pady=16, sticky="w")

        self.theme_switch = customtkinter.CTkSwitch(
            header_card,
            text="Тёмная тема",
            command=self._on_theme_toggle,
            onvalue="dark",
            offvalue="light",
            progress_color=ACCENT_COLOR,
            text_color=TEXT_MUTED,
            font=customtkinter.CTkFont(size=13),
        )
        self.theme_switch.select()
        self.theme_switch.grid(row=0, column=1, padx=20, pady=16, sticky="e")

        # 2. Controls Card
        self.controls_card = customtkinter.CTkFrame(
            self,
            corner_radius=14,
            fg_color=CARD_BG,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self.controls_card.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.controls_card.grid_columnconfigure((0, 2), weight=1)
        self.controls_card.grid_columnconfigure(1, weight=0)

        # Date row
        date_label = customtkinter.CTkLabel(
            self.controls_card,
            text="Дата курса (ДД.ММ.ГГГГ):",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        date_label.grid(row=0, column=0, padx=20, pady=(16, 6), sticky="w")

        date_frame = customtkinter.CTkFrame(self.controls_card, fg_color="transparent")
        date_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 12), sticky="ew")
        date_frame.grid_columnconfigure(0, weight=1)

        self.date_entry = customtkinter.CTkEntry(
            date_frame,
            placeholder_text="04.11.2026",
            height=40,
            font=customtkinter.CTkFont(size=14),
            border_color=CARD_BORDER,
        )
        self.date_entry.grid(row=0, column=0, padx=(0, 12), sticky="ew")
        self.date_entry.bind("<KeyRelease>", self._on_date_entry_changed)
        self.date_entry.bind("<Return>", lambda event: self.fetch_rates_for_current_date())

        self.load_date_button = customtkinter.CTkButton(
            date_frame,
            text="Загрузить курсы",
            width=150,
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=self.fetch_rates_for_current_date,
        )
        self.load_date_button.grid(row=0, column=1, sticky="e")

        # Amount row
        amount_label = customtkinter.CTkLabel(
            self.controls_card,
            text="Сумма для конвертации:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        amount_label.grid(row=2, column=0, padx=20, pady=(4, 6), sticky="w")

        self.amount_entry = customtkinter.CTkEntry(
            self.controls_card,
            placeholder_text="Например: 100 или 10.50",
            height=40,
            font=customtkinter.CTkFont(size=14),
            border_color=CARD_BORDER,
        )
        self.amount_entry.grid(row=3, column=0, columnspan=3, padx=20, pady=(0, 2), sticky="ew")
        self.amount_entry.bind("<KeyRelease>", self._on_amount_changed)

        self.amount_error_label = customtkinter.CTkLabel(
            self.controls_card,
            text="",
            text_color="#EF4444",
            font=customtkinter.CTkFont(size=13),
            wraplength=540,
            justify="left",
            anchor="w",
        )
        self.amount_error_label.grid(row=4, column=0, columnspan=3, padx=20, pady=(2, 10), sticky="w")

        # Currency Selectors row
        curr_label_from = customtkinter.CTkLabel(
            self.controls_card,
            text="Исходная валюта:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        curr_label_from.grid(row=5, column=0, padx=20, pady=(4, 6), sticky="w")

        curr_label_to = customtkinter.CTkLabel(
            self.controls_card,
            text="Целевая валюта:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        curr_label_to.grid(row=5, column=2, padx=20, pady=(4, 6), sticky="w")

        self.source_menu = customtkinter.CTkOptionMenu(
            self.controls_card,
            values=["MDL — Moldovan Leu"],
            command=self._on_currency_changed,
            height=40,
            fg_color=ACCENT_COLOR,
            button_color=ACCENT_HOVER,
            button_hover_color=("#3730A3", "#4338CA"),
            font=customtkinter.CTkFont(size=13),
            dropdown_font=customtkinter.CTkFont(size=13),
        )
        self.source_menu.grid(row=6, column=0, padx=(20, 6), pady=(0, 16), sticky="ew")

        self.swap_button = customtkinter.CTkButton(
            self.controls_card,
            text="⇄",
            width=48,
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            font=customtkinter.CTkFont(size=20, weight="bold"),
            command=self._on_swap_currencies,
        )
        self.swap_button.grid(row=6, column=1, padx=6, pady=(0, 16))

        self.target_menu = customtkinter.CTkOptionMenu(
            self.controls_card,
            values=["MDL — Moldovan Leu"],
            command=self._on_currency_changed,
            height=40,
            fg_color=ACCENT_COLOR,
            button_color=ACCENT_HOVER,
            button_hover_color=("#3730A3", "#4338CA"),
            font=customtkinter.CTkFont(size=13),
            dropdown_font=customtkinter.CTkFont(size=13),
        )
        self.target_menu.grid(row=6, column=2, padx=(6, 20), pady=(0, 16), sticky="ew")

        # Convert button
        self.convert_button = customtkinter.CTkButton(
            self.controls_card,
            text="Конвертировать",
            height=46,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            command=self._on_convert_clicked,
            state="disabled",
            fg_color=DISABLED_BG,
            text_color=DISABLED_TEXT,
        )
        self.convert_button.grid(row=7, column=0, columnspan=3, padx=20, pady=(4, 16), sticky="ew")

        # Loading bar (initially hidden)
        self.loading_bar = customtkinter.CTkProgressBar(
            self.controls_card,
            mode="indeterminate",
            progress_color=ACCENT_COLOR,
        )
        self.loading_bar.grid(row=8, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew")
        self.loading_bar.grid_remove()

        # Status / Feedback label
        self.status_label = customtkinter.CTkLabel(
            self.controls_card,
            text="",
            wraplength=540,
            font=customtkinter.CTkFont(size=13),
            text_color=ACCENT_COLOR,
            justify="left",
            anchor="w",
        )
        self.status_label.grid(row=9, column=0, columnspan=3, padx=20, pady=(0, 14), sticky="w")
        self.status_label.grid_remove()

        # 3. Cache Offer Card (initially hidden, comfortably fits content)
        self.cache_card = customtkinter.CTkFrame(
            self,
            corner_radius=14,
            fg_color=("#FEF3C7", "#2D2415"),
            border_width=1,
            border_color=("#F59E0B", "#B45309"),
        )
        self.cache_card.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.cache_card.grid_columnconfigure(0, weight=1)
        self.cache_card.grid_remove()

        self.cache_message_label = customtkinter.CTkLabel(
            self.cache_card,
            text="",
            wraplength=540,
            font=customtkinter.CTkFont(size=14),
            text_color=("#92400E", "#FDE68A"),
            justify="left",
            anchor="w",
        )
        self.cache_message_label.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="w")

        cache_buttons_frame = customtkinter.CTkFrame(self.cache_card, fg_color="transparent")
        cache_buttons_frame.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")

        self.cache_accept_button = customtkinter.CTkButton(
            cache_buttons_frame,
            text="Использовать кэш",
            command=self._on_cache_accepted,
            height=38,
            width=180,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        self.cache_accept_button.pack(side="left", padx=(0, 12))

        self.cache_decline_button = customtkinter.CTkButton(
            cache_buttons_frame,
            text="Отмена",
            command=self._on_cache_declined,
            height=38,
            width=120,
            fg_color=("#E2E8F0", "#334155"),
            hover_color=("#CBD5E1", "#475569"),
            text_color=TEXT_PRIMARY,
            font=customtkinter.CTkFont(size=14),
        )
        self.cache_decline_button.pack(side="left")

        # 4. Result Card (positioned right under controls card)
        self.result_card = customtkinter.CTkFrame(
            self,
            corner_radius=14,
            fg_color=CARD_BG,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self.result_card.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.result_card.grid_columnconfigure(0, weight=1)

        result_header = customtkinter.CTkLabel(
            self.result_card,
            text="Результат конвертации",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=TEXT_MUTED,
        )
        result_header.grid(row=0, column=0, padx=20, pady=(16, 6), sticky="w")

        # Converted Amount: Large & Bold (~28px)
        self.result_amount_label = customtkinter.CTkLabel(
            self.result_card,
            text="—",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self.result_amount_label.grid(row=1, column=0, padx=20, pady=(2, 6), sticky="w")

        # Directional Rates: Smaller & Muted (~14px)
        self.result_rates_label = customtkinter.CTkLabel(
            self.result_card,
            text="Введите сумму и нажмите «Конвертировать»",
            font=customtkinter.CTkFont(size=14),
            text_color=TEXT_MUTED,
            anchor="w",
            wraplength=540,
            justify="left",
        )
        self.result_rates_label.grid(row=2, column=0, padx=20, pady=(0, 6), sticky="w")

        # Date & Source Attribution: Smaller & Subtle (~12px)
        self.result_meta_label = customtkinter.CTkLabel(
            self.result_card,
            text="",
            font=customtkinter.CTkFont(size=12),
            text_color=TEXT_SUBTLE,
            anchor="w",
        )
        self.result_meta_label.grid(row=3, column=0, padx=20, pady=(0, 16), sticky="w")

    def _on_theme_toggle(self):
        mode = self.theme_switch.get()
        customtkinter.set_appearance_mode(mode)

    def _set_initial_date(self):
        try:
            from zoneinfo import ZoneInfo
            initial = datetime.now(ZoneInfo("Europe/Chisinau")).date()
        except Exception:
            initial = date.today()
        self.date_entry.insert(0, initial.strftime("%d.%m.%Y"))

    def _get_selected_date(self) -> Optional[date]:
        text = self.date_entry.get().strip()
        try:
            return datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            return None

    def _get_selected_codes(self):
        src = self.source_menu.get()
        tgt = self.target_menu.get()
        src_code = src.split(" — ")[0].strip() if src else None
        tgt_code = tgt.split(" — ")[0].strip() if tgt else None
        return src_code, tgt_code

    def _clear_result(self):
        """Clears the old conversion result to avoid showing stale data."""
        self.result_amount_label.configure(text="—")
        self.result_rates_label.configure(text="Введите сумму и нажмите «Конвертировать»")
        self.result_meta_label.configure(text="")

    def _on_date_entry_changed(self, event=None):
        self._clear_result()

    def _on_amount_changed(self, event=None):
        text = self.amount_entry.get()
        if not text.strip():
            self.amount_error_label.configure(text="")
            self._clear_result()
        else:
            try:
                validate_amount(text)
                self.amount_error_label.configure(text="")
            except AmountValidationError as e:
                self.amount_error_label.configure(text=str(e))
                self._clear_result()
        self._update_convert_button_state()

    def _on_currency_changed(self, choice=None):
        self._clear_result()
        self._update_convert_button_state()

    def _update_convert_button_state(self):
        amount = self.amount_entry.get()
        src_code, tgt_code = self._get_selected_codes()
        if self.current_snapshot is not None and can_convert(amount, src_code, tgt_code):
            self.convert_button.configure(
                state="normal",
                fg_color=ACCENT_COLOR,
                hover_color=ACCENT_HOVER,
                text_color="#FFFFFF",
            )
        else:
            self.convert_button.configure(
                state="disabled",
                fg_color=DISABLED_BG,
                text_color=DISABLED_TEXT,
            )

    def _on_swap_currencies(self):
        src = self.source_menu.get()
        tgt = self.target_menu.get()
        self.source_menu.set(tgt)
        self.target_menu.set(src)
        self._clear_result()
        self._update_convert_button_state()

    def fetch_rates_for_current_date(self):
        if self.is_fetching or self.provider is None:
            return

        target_date = self._get_selected_date()
        if target_date is None:
            self.status_label.configure(
                text="Неверный формат даты. Используйте ДД.ММ.ГГГГ.", text_color="#EF4444"
            )
            self.status_label.grid()
            return

        self._clear_result()
        self.is_fetching = True
        self.loading_bar.grid()
        self.loading_bar.start()
        self.load_date_button.configure(state="disabled")
        self._update_convert_button_state()
        self.status_label.configure(
            text="Загрузка официальных курсов валют BNM...", text_color=ACCENT_COLOR
        )
        self.status_label.grid()
        self.cache_card.grid_remove()

        thread = threading.Thread(target=self._worker_fetch_rates, args=(target_date,), daemon=True)
        thread.start()

    def _worker_fetch_rates(self, target_date: date):
        try:
            snapshot = self.provider.get_rates(target_date)
            self.after(0, self._on_rates_fetch_success, target_date, snapshot)
        except (SourceUnavailableError, NoRatesForDateError) as e:
            cached = self.provider.get_cached_rates()
            self.after(0, self._on_rates_fetch_failure, e, cached)
        except Exception as e:
            cached = self.provider.get_cached_rates()
            self.after(0, self._on_rates_fetch_failure, e, cached)

    def _on_rates_fetch_success(self, requested_date: date, snapshot: RateSnapshot):
        if not self.winfo_exists():
            return
        self.is_fetching = False
        self.loading_bar.stop()
        self.loading_bar.grid_remove()
        self.load_date_button.configure(state="normal")

        self.current_snapshot = snapshot
        self._populate_currencies(snapshot)

        if requested_date != snapshot.rate_date:
            msg = format_fallback_message(requested_date, snapshot.rate_date)
            self.status_label.configure(text=msg, text_color=("#D97706", "#F59E0B"))
            self.status_label.grid()
        else:
            self.status_label.configure(
                text=f"Курсы за {snapshot.rate_date.strftime('%d.%m.%Y')} успешно загружены.",
                text_color=("#16A34A", "#22C55E"),
            )
            self.status_label.grid()

        self._update_convert_button_state()

    def _on_rates_fetch_failure(self, error: Exception, cached_snapshot: Optional[RateSnapshot]):
        if not self.winfo_exists():
            return
        self.is_fetching = False
        self.loading_bar.stop()
        self.loading_bar.grid_remove()
        self.load_date_button.configure(state="normal")
        self._update_convert_button_state()

        if cached_snapshot is not None:
            self.pending_cache_snapshot = cached_snapshot
            msg = format_error_message("cache_available", cache_date=cached_snapshot.rate_date)
            self.cache_message_label.configure(text=msg)
            self.cache_card.grid()
            self.status_label.configure(
                text="Не удалось получить курсы из сети.", text_color="#EF4444"
            )
            self.status_label.grid()
        else:
            msg = format_error_message("no_cache")
            self.status_label.configure(text=msg, text_color="#EF4444")
            self.status_label.grid()

    def _on_cache_accepted(self):
        if self.pending_cache_snapshot is not None:
            self.current_snapshot = self.pending_cache_snapshot
            self._populate_currencies(self.current_snapshot)
            date_str = self.current_snapshot.rate_date.strftime("%d.%m.%Y")
            self.status_label.configure(
                text=f"Используются сохраненные курсы из кэша за {date_str}.",
                text_color=ACCENT_COLOR,
            )
            self.status_label.grid()
            self.cache_card.grid_remove()
            self._clear_result()
            self._update_convert_button_state()

    def _on_cache_declined(self):
        self.pending_cache_snapshot = None
        self.cache_card.grid_remove()
        self.status_label.configure(
            text="Использование кэша отклонено пользователем.", text_color=TEXT_MUTED
        )
        self.status_label.grid()

    def _populate_currencies(self, snapshot: RateSnapshot):
        current_src, current_tgt = self._get_selected_codes()

        items = []
        for code, curr in sorted(snapshot.currencies.items(), key=lambda x: (x[0] != "MDL", x[0])):
            label = f"{curr.code} — {curr.name}"
            items.append(label)

        self.source_menu.configure(values=items)
        self.target_menu.configure(values=items)

        default_src = next((i for i in items if i.startswith(f"{current_src} — ")), None)
        default_tgt = next((i for i in items if i.startswith(f"{current_tgt} — ")), None)

        if not default_src:
            default_src = next((i for i in items if i.startswith("EUR — ")), items[0])
        if not default_tgt:
            default_tgt = next((i for i in items if i.startswith("MDL — ")), items[-1])

        self.source_menu.set(default_src)
        self.target_menu.set(default_tgt)
        self._update_convert_button_state()

    def _on_convert_clicked(self):
        if self.current_snapshot is None:
            return

        amount_str = self.amount_entry.get().strip()
        try:
            amount = validate_amount(amount_str)
        except AmountValidationError as e:
            self.amount_error_label.configure(text=str(e))
            self._clear_result()
            return

        src_code, tgt_code = self._get_selected_codes()
        if not src_code or not tgt_code:
            return

        try:
            result = convert(amount, src_code, tgt_code, self.current_snapshot)
            # Display formatted values
            self.result_amount_label.configure(text=f"{result.converted_amount} {tgt_code}")
            self.result_rates_label.configure(
                text=f"1 {src_code} = {result.source_to_target_rate} {tgt_code}   •   1 {tgt_code} = {result.target_to_source_rate} {src_code}"
            )
            date_str = result.snapshot_date.strftime("%d.%m.%Y")
            self.result_meta_label.configure(
                text=f"Официальный курс BNM на {date_str}   |   Источник: {result.source}"
            )
        except Exception as e:
            self.result_amount_label.configure(text="Ошибка")
            self.result_rates_label.configure(text=f"Ошибка конвертации: {e}")
            self.result_meta_label.configure(text="")
