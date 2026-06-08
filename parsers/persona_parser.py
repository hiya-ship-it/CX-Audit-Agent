"""
Persona Parser
--------------
Reads a Markdown file and converts each '## Persona:' block into a
structured Persona dataclass. No hardcoded field names — every list-item
key/value pair is captured generically, with well-known fields surfaced
as typed attributes for the rest of the system to use.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional
from slugify import slugify


# City → representative pincode
_LOCATION_PINCODES: dict[str, str] = {
    "mumbai": "400001", "delhi": "110001", "bangalore": "560001",
    "bengaluru": "560001", "chennai": "600001", "kolkata": "700001",
    "hyderabad": "500001", "pune": "411001", "ahmedabad": "380001",
    "surat": "395001", "jaipur": "302001", "lucknow": "226001",
    "kanpur": "208001", "nagpur": "440001", "indore": "452001",
    "thane": "400601", "bhopal": "462001", "visakhapatnam": "530001",
    "patna": "800001", "vadodara": "390001", "ghaziabad": "201001",
    "agra": "282001", "nashik": "422001", "ranchi": "834001",
    "faridabad": "121001", "meerut": "250001", "rajkot": "360001",
    "jodhpur": "342001", "raipur": "492001", "kota": "324001",
    "guwahati": "781001", "chandigarh": "160001", "shimla": "171001",
    "dehradun": "248001", "amritsar": "143001", "allahabad": "211001",
    "prayagraj": "211001", "coimbatore": "641001", "madurai": "625001",
    "varanasi": "221001", "noida": "201301", "gurugram": "122001",
    "gurgaon": "122001",
}


_PRODUCT_KEYWORDS: dict[str, list[str]] = {
    "Personal Loan":         [" personal loan", " pl loan", " salaried loan", " salary loan"],
    "Business Loan":         [" business loan", " sme loan", " msme loan", " working capital"],
    "Home Loan":             [" home loan", " housing loan", " property loan", " home finance"],
    "Loan Against Property": [" loan against property", " lap loan"],
    "Gold Loan":             [" gold loan"],
    "Education Loan":        [" education loan", " student loan", " study loan"],
    "Two-Wheeler Loan":      [" two-wheeler", " two wheeler", " bike loan", " motorcycle loan", " scooter loan"],
    "Car Loan":              [" car loan", " auto loan", " vehicle loan", " used car"],
    "Credit Card":           [" credit card", " bajaj card"],
    "Insurance":             [" insurance", " life cover", " term plan", " term insurance", " health cover"],
    "Fixed Deposit":         [" fixed deposit", " term deposit", " fd "],
    "Mutual Funds":          [" mutual fund", " sip ", " investment fund"],
    "Flexi Loan":            [" flexi loan", " flexi-loan", " line of credit"],
    "Consumer Durable Loan": [" consumer durable", " appliance loan", " electronics loan"],
    "Online Shopping / EMI": [" no-cost emi", " zero cost emi", " buy now pay later", " bnpl", " emi on "],
    "Pocket Insurance":      [" pocket insurance", " micro insurance", " bite-size insurance"],
    "Doctor Loan":           [" doctor loan", " medical professional loan"],
}


@dataclass
class Persona:
    # Well-known typed fields
    name:               str = ""
    age:                Optional[int] = None
    gender:             Optional[str] = None
    occupation:         Optional[str] = None
    location:           Optional[str] = None
    device:             Optional[str] = None
    financial_literacy: Optional[str] = None
    intent:             str = ""
    constraints:        Optional[str] = None
    behaviour:          Optional[str] = None
    success_criteria:   Optional[str] = None
    patience:           Optional[str] = None   # "low" | "medium" | "high"
    navigation_style:   Optional[str] = None   # "search-first" | "browse-nav" | "scroll-explore"
    dropout_trigger:    Optional[str] = None   # free-text: what frustrates this persona

    # Everything from the .md block, keyed by normalised label
    raw_attributes: dict[str, str] = field(default_factory=dict)

    def infer_product(self) -> str:
        """Keyword-match persona intent + background against BFL product taxonomy."""
        text = " " + " ".join([
            self.intent or "",
            self.raw_attributes.get("background", ""),
            self.constraints or "",
            self.raw_attributes.get("product", ""),
        ]).lower() + " "
        for product, keywords in _PRODUCT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return product
        return "General"

    @property
    def slug(self) -> str:
        return slugify(self.name)

    def to_prompt_block(self) -> str:
        lines = [f"PERSONA: {self.name}"]
        if self.age:
            lines.append(f"  Age: {self.age}")
        if self.gender:
            lines.append(f"  Gender: {self.gender}")
        if self.occupation:
            lines.append(f"  Occupation: {self.occupation}")
        if self.location:
            lines.append(f"  Location: {self.location}")
        if self.financial_literacy:
            lines.append(f"  Financial literacy: {self.financial_literacy}")
        lines.append(f"  Goal / intent: {self.intent}")
        if self.constraints:
            lines.append(f"  Constraints: {self.constraints}")
        if self.behaviour:
            lines.append(f"  Typical behaviour: {self.behaviour}")
        if self.success_criteria:
            lines.append(f"  Success criteria: {self.success_criteria}")
        if self.patience:
            lines.append(f"  Patience level: {self.patience}")
        if self.navigation_style:
            lines.append(f"  Navigation style: {self.navigation_style}")
        if self.dropout_trigger:
            lines.append(f"  Dropout trigger: {self.dropout_trigger}")

        # Include any extra raw attributes not captured above
        known_keys = {
            "age", "gender", "occupation", "location", "device",
            "financial literacy", "intent", "constraints", "behaviour",
            "behavior", "success criteria", "background",
            "patience", "navigation style", "dropout trigger",
        }
        for k, v in self.raw_attributes.items():
            if k not in known_keys and v:
                lines.append(f"  {k.title()}: {v}")
        return "\n".join(lines)

    def get_test_data(self) -> dict:
        """
        Deterministic test data for form filling during audits.
        Uses persona name as RNG seed so each persona always gets the same data.
        DOB is back-calculated from age with random day/month.
        Income is extracted from persona attributes or inferred from occupation.
        Phone is a generic dummy — for logged-in journeys the user enters their
        real number manually in the browser window.
        """
        rng = random.Random(hash(self.name) & 0x7FFFFFFF)

        # ── Phone — generic dummy, never triggers a real OTP ──────────────────
        phone = "9999999999"

        # ── Date of birth ─────────────────────────────────────────────────────
        current_year = date.today().year
        birth_year   = current_year - (self.age or 30)
        birth_month  = rng.randint(1, 12)
        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
        }
        birth_day = rng.randint(1, days_in_month.get(birth_month, 28))

        # ── Income ────────────────────────────────────────────────────────────
        monthly_income = self._infer_monthly_income(rng)

        # ── Pincode ───────────────────────────────────────────────────────────
        pincode = self._infer_pincode()

        return {
            "phone":          phone,
            "dob":            f"{birth_day:02d}/{birth_month:02d}/{birth_year}",
            "dob_dd":         f"{birth_day:02d}",
            "dob_mm":         f"{birth_month:02d}",
            "dob_yyyy":       str(birth_year),
            "monthly_income": monthly_income,
            "annual_income":  monthly_income * 12,
            "email":          f"test.{re.sub(r'[^a-z0-9]', '', self.slug[:12])}@gmail.com",
            "pincode":        pincode,
            "pan":            "ABCDE1234F",
            "full_name":      self.name.split(" - ")[0].strip() if " - " in self.name else self.name,
        }

    def _infer_monthly_income(self, rng: random.Random) -> int:
        # 1. Try explicit income fields
        for key in ["income", "monthly income", "salary", "monthly salary", "earning"]:
            val = self.raw_attributes.get(key, "").lower()
            if val:
                parsed = _parse_rupee_amount(val)
                if parsed:
                    # If likely annual (> 3 lakh), convert to monthly
                    return parsed // 12 if parsed > 300000 else parsed

        # 2. Try extracting from constraints/background text
        combined = " ".join([
            self.constraints or "",
            self.raw_attributes.get("background", ""),
            self.raw_attributes.get("income", ""),
        ]).lower()

        m = re.search(
            r'(?:income|salary|earn[s]?|earning)\s*(?:of|is|:)?\s*[₹]?\s*([\d,]+)\s*(k|lakh|l\b)?',
            combined,
        )
        if m:
            num = int(m.group(1).replace(",", ""))
            suffix = (m.group(2) or "").lower()
            if suffix in ("k",):
                num *= 1000
            elif suffix in ("lakh", "l"):
                num = num * 100000 // 12  # convert annual lakh to monthly
            return num if num > 5000 else num * 1000

        # 3. Infer from occupation + background
        occ = (self.occupation or "").lower()
        bg  = self.raw_attributes.get("background", "").lower()
        ctx = occ + " " + bg

        if any(x in ctx for x in ["construction", "daily wage", "labour", "casual worker", "mazdoor"]):
            return rng.randint(12000, 18000)
        if any(x in ctx for x in ["auto", "driver", "delivery", "hawker", "vegetable vendor"]):
            return rng.randint(15000, 25000)
        if any(x in ctx for x in ["farmer", "agriculture", "kisan"]):
            return rng.randint(8000, 20000)
        if any(x in ctx for x in ["shopkeeper", "kirana", "retailer", "small shop"]):
            return rng.randint(20000, 40000)
        if any(x in ctx for x in ["teacher", "nurse", "nursing", "school"]):
            return rng.randint(25000, 45000)
        if any(x in ctx for x in ["government", "sarkari", "peon", "clerk", "babu"]):
            return rng.randint(20000, 35000)
        if any(x in ctx for x in ["engineer", "it ", "software", "developer", "programmer", "tech"]):
            return rng.randint(50000, 100000)
        if any(x in ctx for x in ["manager", "executive", "head of", "director"]):
            return rng.randint(60000, 150000)
        if any(x in ctx for x in ["doctor", "ca ", "chartered", "lawyer", "consultant", "advocate"]):
            return rng.randint(80000, 200000)
        if any(x in ctx for x in ["business owner", "entrepreneur", "proprietor"]):
            return rng.randint(40000, 120000)
        if any(x in ctx for x in ["housewife", "homemaker", "home maker"]):
            return 0
        if any(x in ctx for x in ["retired", "pensioner", "senior citizen"]):
            return rng.randint(15000, 40000)

        return rng.randint(20000, 40000)

    def _infer_pincode(self) -> str:
        loc = (self.location or "").lower()
        for city, pin in _LOCATION_PINCODES.items():
            if city in loc:
                return pin
        return "110001"

    def __str__(self) -> str:
        return f"Persona({self.name!r}, intent={self.intent!r})"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_rupee_amount(text: str) -> Optional[int]:
    """Parse rupee amount strings like '₹15K', '15,000', '1.5 lakh'."""
    text = text.replace("₹", "").replace(",", "").strip()
    m = re.search(r'(\d+(?:\.\d+)?)\s*(k|lakh|l\b|cr)?', text, re.I)
    if not m:
        return None
    num    = float(m.group(1))
    suffix = (m.group(2) or "").lower()
    if suffix == "k":
        return int(num * 1000)
    if suffix in ("lakh", "l"):
        return int(num * 100000)
    if suffix == "cr":
        return int(num * 10000000)
    return int(num) if num > 100 else int(num * 1000)


# ── Well-known field mapping ──────────────────────────────────────────────────

_WELL_KNOWN: dict[str, str] = {
    "age":               "age",
    "gender":            "gender",
    "occupation":        "occupation",
    "location":          "location",
    "device":            "device",
    "financial literacy": "financial_literacy",
    "intent":            "intent",
    "constraints":       "constraints",
    "behaviour":         "behaviour",
    "behavior":          "behaviour",
    "success criteria":  "success_criteria",
    "patience":          "patience",
    "navigation style":  "navigation_style",
    "dropout trigger":   "dropout_trigger",
}


def _normalise_key(raw: str) -> str:
    return raw.strip().lower()


def _parse_block(header: str, body: str) -> Persona:
    persona = Persona(name=header.strip())

    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line.lstrip("- ").strip()
        if ":" not in line:
            continue

        raw_key, _, raw_val = line.partition(":")
        key = _normalise_key(raw_key)
        val = raw_val.strip()

        persona.raw_attributes[key] = val

        mapped = _WELL_KNOWN.get(key)
        if mapped == "age":
            try:
                persona.age = int(re.search(r"\d+", val).group())
            except (AttributeError, ValueError):
                pass
        elif mapped and mapped != "age":
            setattr(persona, mapped, val)

    persona.raw_attributes["product"] = persona.infer_product()
    return persona


# ── Public API ────────────────────────────────────────────────────────────────

class PersonaParser:

    @staticmethod
    def parse(path: str | Path) -> list[Persona]:
        text = Path(path).read_text(encoding="utf-8")
        personas: list[Persona] = []

        pattern = re.compile(r"^##\s*Persona(?:\s+\d+)?:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
        matches = list(pattern.finditer(text))

        for i, match in enumerate(matches):
            header = match.group(1)
            start  = match.end()
            end    = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body   = text[start:end]
            p = _parse_block(header, body)
            if p.name and p.intent:
                personas.append(p)

        if not personas:
            raise ValueError(
                f"No valid persona blocks found in {path!r}. "
                "Each block must start with '## Persona:' and include an '- Intent:' line."
            )

        return personas
