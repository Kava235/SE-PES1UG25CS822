"""Insurance premium calculator: quotes, imports and renewal helpers."""
import csv
import hmac
import logging
import os
import secrets
import ssl
import tarfile
import tempfile
import urllib.request
from dataclasses import dataclass
from datetime import datetime

from defusedxml import ElementTree as ET

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)

# Global quote book
QUOTES = {}
HOST = "127.0.0.1"
# Secret comes from the environment, never from source code.
UNDERWRITER_TOKEN = os.environ.get("UNDERWRITER_TOKEN", "")
LOG_FILE = os.path.join(tempfile.gettempdir(), "premium_quotes.log")
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}


@dataclass
class Applicant:
    """Details of the person being quoted."""

    policy_type: str
    age: int
    sum_insured: int
    smoker: bool
    claims: int


def calculate_premium(applicant, discounts=None):
    """Return the premium for an applicant, never below zero."""
    if not isinstance(applicant.smoker, bool):
        raise TypeError("smoker must be True or False")
    discounts = discounts or []
    premium = BASE_RATES[applicant.policy_type]
    premium += applicant.sum_insured * 0.002
    if applicant.age > 45:
        premium *= 1.5
    if applicant.smoker:
        premium *= 1.3
    premium += applicant.claims * 1000
    premium -= sum(discounts)
    return max(premium, 0.0)


def age_from_dob(dob):
    """Return age in whole years from a DD-MM-YYYY date of birth."""
    born = datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.now()
    had_birthday = (today.month, today.day) >= (born.month, born.day)
    return today.year - born.year - (0 if had_birthday else 1)


def policy_number():
    """Return a random policy number that is not already in use."""
    while True:
        number = "POL-" + str(secrets.randbelow(900000) + 100000)
        if number not in QUOTES:
            return number


def save_quote(name, premium):
    """Store a quote in memory and append it to the log file."""
    number = policy_number()
    QUOTES[number] = {"name": name, "premium": premium}
    with open(LOG_FILE, "a", encoding="utf-8", newline="") as log:
        csv.writer(log).writerow([number, name, f"{premium:.2f}"])
    return number


def import_policies(xml_text):
    """Parse partner XML into (type, age, sum) tuples, skipping bad rows."""
    root = ET.fromstring(xml_text)
    result = []
    for policy in root.findall("policy"):
        try:
            result.append((policy.get("type"), int(policy.get("age")),
                           int(policy.get("sum"))))
        except (TypeError, ValueError):
            LOGGER.warning("Skipping invalid policy: %s", policy.attrib)
    return result


def fetch_rates(url):
    """Download a rate table over HTTPS with certificate checking."""
    if not url.lower().startswith("https://"):
        raise ValueError("Only https:// URLs are allowed")
    ctx = ssl.create_default_context()
    # Scheme is checked above, so file:/ and custom schemes are rejected.
    with urllib.request.urlopen(url, context=ctx) as resp:  # nosec B310
        return resp.read()


def import_claim_documents(archive_path):
    """Extract a customer-uploaded archive without unsafe members."""
    with tarfile.open(archive_path) as tar:
        tar.extractall("claims_docs", filter="data")


def monthly_instalment(premium, months=12):
    """Split a premium into equal instalments, rounded to paise."""
    if months < 0:
        raise ValueError("months cannot be negative")
    if months == 0:
        return premium
    return round(premium / months, 2)


def is_authorised(token):
    """Check an underwriter token using a constant-time comparison."""
    if not UNDERWRITER_TOKEN:
        return False
    return hmac.compare_digest(token.encode(), UNDERWRITER_TOKEN.encode())


def renewal_due(start, years=1):
    """Return the renewal date; 29 Feb moves to 28 Feb in non-leap years."""
    date = datetime.strptime(start, "%Y-%m-%d")
    try:
        renewed = date.replace(year=date.year + years)
    except ValueError:
        renewed = date.replace(year=date.year + years, day=28)
    return renewed.strftime("%Y-%m-%d")


def print_quotes():
    """Print every saved quote."""
    print("===== Quote Book =====")
    for i, (number, quote) in enumerate(QUOTES.items(), start=1):
        print(i, number, quote["name"], "Rs.", quote["premium"])


def main():
    """Run a demo of the calculator."""
    health = Applicant("health", 30, 500000, False, 0)
    motor = Applicant("motor", 50, 800000, False, 0)
    life = Applicant("life", 25, 100000, False, 0)
    p1 = calculate_premium(health)
    p2 = calculate_premium(health)
    p3 = calculate_premium(motor)
    p4 = calculate_premium(life, [3000, 3000, 3000])
    print("Quote 1:", p1)
    print("Quote 2 (same customer details):", p2)
    print("Non-smoker aged 50:", p3)
    print("Life with stacked discounts:", p4)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(p3))
    print("Renewal due:", renewal_due("2025-03-15"))
    print("Imported:", import_policies(
        "<policies><policy type='health' age='40' sum='300000'/>"
        "<policy type='motor' age='abc' sum='1'/></policies>"))
    print("Saved as:", save_quote("Kiran", p1))
    print("Authorised:", is_authorised("uw-7f3a9c2e1b"))
    print("Server would listen on", HOST)
    print_quotes()


if __name__ == "__main__":
    main()
