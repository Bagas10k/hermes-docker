"""Indonesian locale OCR dialect and noise tolerance analyzer (BIZ-011).

Evaluates and normalizes Rupiah (id_ID) and foreign (en_US) numeric tokens under:
1. Punctuation speckle / double separators (e.g. '1..234.567', '1.234..567,00')
2. Indonesian suffix conventions (e.g. '1.234.567,-' or '1.234.567,--')
3. Currency prefix intrusions (e.g. 'Rp', 'Rp.', 'IDR', '$', 'USD')
4. Whitespace / kerning breaks (e.g. '1 234 567', '1.234. 567', '1. 234.567')
5. Ambiguous grouping vs decimal period detection (e.g. '1.23.456', '12.345.6')

Contractual Invariants:
- A token is clean if it strictly conforms to locale grammar without repair.
- A token repaired via deterministic OCR rules is marked 'repaired_token' and forces 'requires_review: True'.
- An irrecoverable token (e.g. irregular group lengths) produces no decimal value and forces 'requires_review: True'.
- Zero arithmetic tolerance; all normalized numbers parse to exact Python Decimal.
"""
from decimal import Decimal
import re
from typing import Dict, Any, List, Optional


class IndonesianLocaleOCRNormalizer:
    def __init__(self):
        pass

    @classmethod
    def inspect_and_clean(cls, raw: str, locale: str = "id_ID") -> Dict[str, Any]:
        """Inspects token for OCR artifacts and attempts deterministic cleaning.
        Returns:
            {
                "original": raw,
                "cleaned": str or None,
                "decimal_value": Decimal or None,
                "anomalies": list[str],
                "requires_review": bool
            }
        """
        if locale not in ("en_US", "id_ID"):
            raise ValueError(f"unsupported locale: {locale}")

        anomalies: List[str] = []
        token = raw.strip()

        # 1. Currency prefix detection & normalization
        prefix_pattern = r'^(?:(?:Rp|IDR|USD|\$)\.?\s*)'
        prefix_match = re.search(prefix_pattern, token, re.IGNORECASE)
        if prefix_match:
            detected_prefix = prefix_match.group(0).strip()
            anomalies.append(f"currency_prefix_removed:{detected_prefix}")
            token = re.sub(prefix_pattern, '', token, flags=re.IGNORECASE).strip()

        # 2. Indonesian dash / nil decimal suffix: ',-' or ',--'
        if locale == "id_ID":
            if re.search(r',-+$', token):
                anomalies.append("dash_cents_suffix_normalized")
                token = re.sub(r',-+$', ',00', token)
        elif locale == "en_US":
            if re.search(r'\.-+$', token):
                anomalies.append("dash_cents_suffix_normalized")
                token = re.sub(r'\.-+$', '.00', token)

        # 3. Double punctuation / speckle noise (e.g. '..', ',,')
        if ".." in token:
            anomalies.append("speckle_double_period_collapsed")
            token = re.sub(r'\.{2,}', '.', token)
        if ",," in token:
            anomalies.append("speckle_double_comma_collapsed")
            token = re.sub(r',{2,}', ',', token)

        # 4. Whitespace inside number (scanning jitter / kerning)
        if re.search(r'\d\s+[.,]\s*\d', token) or re.search(r'\d\s*[.,]\s+\d', token):
            anomalies.append("whitespace_around_separator_collapsed")
            token = re.sub(r'\s*([.,])\s*', '\\1', token)
        elif re.search(r'\d\s+\d', token):
            anomalies.append("internal_whitespace_collapsed")
            token = re.sub(r'\s+', '', token)

        # 5. Group and decimal separator assignments
        group_char, dec_char = ('.', ',') if locale == "id_ID" else (',', '.')

        # Strict regex pattern
        strict_pattern = rf'(?:[0-9]{{1,12}}|[0-9]{{1,3}}(?:{re.escape(group_char)}[0-9]{{3}}){{1,3}})(?:{re.escape(dec_char)}[0-9]{{1,4}})?'
        is_clean_match = bool(re.fullmatch(strict_pattern, token))

        # Irregular grouping check
        has_irregular_grouping = False
        parts = token.split(dec_char)[0].split(group_char)
        if len(parts) > 1:
            for p in parts[1:]:
                if len(p) != 3:
                    has_irregular_grouping = True
                    anomalies.append(f"irregular_grouping_length:{len(p)}")
                    break

        requires_review = False
        cleaned_val: Optional[str] = None
        dec_val: Optional[Decimal] = None

        if is_clean_match and not has_irregular_grouping:
            cleaned_val = token
            standard_num_str = token.replace(group_char, '').replace(dec_char, '.')
            dec_val = Decimal(standard_num_str)
            if anomalies:
                requires_review = True
        else:
            requires_review = True
            anomalies.append("strict_grammar_mismatch")

        return {
            "original": raw,
            "cleaned": cleaned_val,
            "decimal_value": dec_val,
            "anomalies": anomalies,
            "requires_review": requires_review or bool(anomalies)
        }

    @classmethod
    def parse_with_tolerance(cls, raw: str, locale: str = "id_ID") -> tuple[Decimal, list[str]]:
        """Parses a raw string into Decimal, returning (Decimal, anomalies).
        Raises ValueError if unrecoverable.
        """
        res = cls.inspect_and_clean(raw, locale)
        if res["decimal_value"] is None:
            raise ValueError(f"Unrecoverable number: {raw!r} ({res['anomalies']})")
        return res["decimal_value"], res["anomalies"]
