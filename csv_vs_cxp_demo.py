# ============================================================
#  CSV vs CXP SECURE TRANSFER — SIDE BY SIDE DEMO
#  ZeroKey Project | Koushik | 2026
#  Run this on Google Colab — no installation needed
# ============================================================
#
#  This demo shows exactly why the current CSV credential
#  export method is dangerously insecure — and how the FIDO
#  Alliance's Credential Exchange Protocol (CXP) solves it
#  using real Diffie-Hellman cryptography.
#
# ============================================================

# ── INSTALL REQUIRED LIBRARY ────────────────────────────────
# (cryptography library is pre-installed on Google Colab)
# If running locally: pip install cryptography

import csv
import io
import os
import json
import hashlib
import secrets
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ── VISUAL HELPERS ───────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
DIM    = "\033[2m"

def banner(text, color=CYAN):
    width = 62
    print()
    print(color + "═" * width + RESET)
    padding = (width - len(text) - 2) // 2
    print(color + "║" + " " * padding + BOLD + text + RESET + color + " " * (width - padding - len(text) - 1) + "║" + RESET)
    print(color + "═" * width + RESET)
    print()

def section(text, color=YELLOW):
    print()
    print(color + BOLD + f"  ▶  {text}" + RESET)
    print(color + "  " + "─" * 56 + RESET)

def info(label, value, color=WHITE):
    print(f"  {DIM}{label:<28}{RESET}{color}{value}{RESET}")

def attacker_sees(text):
    print(f"\n  {RED}{BOLD}⚠  ATTACKER INTERCEPTS:{RESET}")
    print(f"  {RED}{'─' * 54}{RESET}")
    for line in text.strip().split("\n"):
        print(f"  {RED}{line}{RESET}")
    print(f"  {RED}{'─' * 54}{RESET}\n")

def success(text):
    print(f"  {GREEN}{BOLD}✔  {text}{RESET}")

def fail(text):
    print(f"  {RED}{BOLD}✘  {text}{RESET}")

def step(n, text):
    print(f"\n  {CYAN}{BOLD}[STEP {n}]{RESET}  {text}")

def divider():
    print(f"\n  {DIM}{'·' * 58}{RESET}\n")


# ════════════════════════════════════════════════════════════
#  SAMPLE CREDENTIALS
#  (Fictional users — used for demonstration only)
# ════════════════════════════════════════════════════════════

CREDENTIALS = [
    {"user": "alice@gmail.com",   "service": "Gmail",    "password": "Sunshine@2024",  "passkey_id": "pk_a1b2c3"},
    {"user": "bob@outlook.com",   "service": "Outlook",  "password": "Dragon$Fire99",  "passkey_id": "pk_d4e5f6"},
    {"user": "carol@yahoo.com",   "service": "Yahoo",    "password": "Tr0ub4dor&3",    "passkey_id": "pk_g7h8i9"},
    {"user": "dave@icloud.com",   "service": "iCloud",   "password": "Correct-Horse1", "passkey_id": "pk_j0k1l2"},
    {"user": "emma@proton.me",    "service": "ProtonMail","password": "Purple!Rain77",  "passkey_id": "pk_m3n4o5"},
]


# ════════════════════════════════════════════════════════════
#  ACT 1 — THE CSV PROBLEM
# ════════════════════════════════════════════════════════════

def act_one_csv():
    banner("ACT 1 — CSV EXPORT: THE BROKEN METHOD", RED)

    print(f"  {WHITE}Scenario: A user wants to move their credentials from")
    print(f"  Google Password Manager to Bitwarden.")
    print(f"  They use the standard CSV export method.{RESET}\n")

    # ── Step 1: Export
    section("Step 1 — Exporting credentials as CSV")
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["user", "service", "password", "passkey_id"])
    writer.writeheader()
    for cred in CREDENTIALS:
        writer.writerow(cred)
    csv_content = csv_buffer.getvalue()

    success("CSV file created: credentials_export.csv")
    info("File format", "Plain text — no encryption")
    info("File protection", "None")
    info("Credentials inside", str(len(CREDENTIALS)))
    divider()

    # ── Step 2: The file travels (gets intercepted)
    section("Step 2 — File travels to new provider (intercepted)")
    print(f"  {WHITE}The CSV file must be physically moved — downloaded to")
    print(f"  the device, then uploaded to the new provider.")
    print(f"  During this journey, it sits unprotected on the device.{RESET}\n")

    attacker_sees(csv_content)

    fail("Attacker reads EVERY credential instantly")
    fail("All 5 users' passwords exposed in plain text")
    fail("All passkey IDs exposed — can be used for account enumeration")
    fail("No cryptography was broken — the file was just... readable")
    divider()

    # ── Step 3: Damage summary
    section("Step 3 — What the attacker now has")
    print()
    for cred in CREDENTIALS:
        print(f"  {RED}●  {cred['user']:<28} Password: {cred['password']}{RESET}")
    print()
    fail("Transfer success rate for attacker: 100%")
    fail("Time required to steal all credentials: < 1 second")
    fail("Technical skill required: None — it's a plain text file")

    return csv_content


# ════════════════════════════════════════════════════════════
#  ACT 2 — THE CXP SOLUTION
#  Using real X25519 Diffie-Hellman + AES-256-GCM encryption
# ════════════════════════════════════════════════════════════

def act_two_cxp():
    banner("ACT 2 — CXP SECURE TRANSFER: THE REAL METHOD", GREEN)

    print(f"  {WHITE}Same scenario. Same credentials. Same attacker.")
    print(f"  But this time — the FIDO Alliance's Credential Exchange")
    print(f"  Protocol (CXP) is used instead of CSV.{RESET}\n")

    # ── Step 1: Both providers generate X25519 key pairs
    section("Step 1 — Diffie-Hellman Key Exchange Begins")
    print(f"\n  {WHITE}Provider A (Google) and Provider B (Bitwarden) each")
    print(f"  generate their own private and public key pair.")
    print(f"  Public keys are exchanged openly — anyone can see them.")
    print(f"  Private keys NEVER leave their respective providers.{RESET}\n")

    step(1, "Provider A generates X25519 key pair")
    private_key_a = X25519PrivateKey.generate()
    public_key_a  = private_key_a.public_key()
    pub_a_bytes   = public_key_a.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw
    )
    info("Provider A private key", "[locked inside Provider A — never shared]", DIM)
    info("Provider A public key",  pub_a_bytes.hex()[:32] + "...", CYAN)

    step(2, "Provider B generates X25519 key pair")
    private_key_b = X25519PrivateKey.generate()
    public_key_b  = private_key_b.public_key()
    pub_b_bytes   = public_key_b.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw
    )
    info("Provider B private key", "[locked inside Provider B — never shared]", DIM)
    info("Provider B public key",  pub_b_bytes.hex()[:32] + "...", CYAN)

    step(3, "Public keys are exchanged — attacker can see these")
    print(f"\n  {YELLOW}  Attacker intercepts public key exchange:{RESET}")
    print(f"  {YELLOW}  A→B: {pub_a_bytes.hex()[:48]}...{RESET}")
    print(f"  {YELLOW}  B→A: {pub_b_bytes.hex()[:48]}...{RESET}")
    print(f"\n  {DIM}  Attacker has both public keys. Useless without private keys.{RESET}\n")

    divider()

    # ── Step 2: Shared secret derived independently on both sides
    section("Step 2 — Shared Secret Derived (Never Transmitted)")

    step(4, "Provider A computes shared secret using B's public key")
    shared_secret_a = private_key_a.exchange(public_key_b)

    step(5, "Provider B computes shared secret using A's public key")
    shared_secret_b = private_key_b.exchange(public_key_a)

    step(6, "Verify both sides arrived at the SAME secret")
    match = shared_secret_a == shared_secret_b
    if match:
        success("Shared secrets MATCH — Diffie-Hellman successful")
        info("Shared secret (first 32 chars)", shared_secret_a.hex()[:32] + "...", GREEN)
        info("Was the secret ever transmitted?", "NO — computed independently on both sides", GREEN)
    else:
        fail("Shared secrets do not match — something went wrong")
        return

    divider()

    # ── Step 3: Derive encryption key using HKDF
    section("Step 3 — Derive AES-256 Encryption Key via HKDF")
    print(f"\n  {WHITE}Raw shared secrets are not used directly for encryption.")
    print(f"  HKDF (HMAC-based Key Derivation Function) converts the")
    print(f"  shared secret into a proper AES-256-GCM encryption key.{RESET}\n")

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"CXP-credential-transfer-v1"
    )
    encryption_key = hkdf.derive(shared_secret_a)

    info("Derived AES-256 key", encryption_key.hex()[:32] + "...", GREEN)
    info("Key derivation method", "HKDF-SHA256")
    info("Key length", "256 bits (32 bytes)")
    divider()

    # ── Step 4: Encrypt credentials using AES-256-GCM
    section("Step 4 — Credentials Encrypted Using AES-256-GCM")

    # Serialize credentials to JSON (this is the CXF formatted payload)
    payload = json.dumps({
        "version": "CXF-v1.0",
        "provider": "Google Password Manager",
        "credentials": CREDENTIALS
    }).encode()

    aesgcm   = AESGCM(encryption_key)
    nonce    = secrets.token_bytes(12)          # 96-bit random nonce
    encrypted_payload = aesgcm.encrypt(nonce, payload, None)

    success("Credentials encrypted with AES-256-GCM")
    info("Original payload size", f"{len(payload)} bytes")
    info("Encrypted payload size", f"{len(encrypted_payload)} bytes")
    info("Nonce (random, one-time)", nonce.hex())
    divider()

    # ── Step 5: Attacker intercepts — sees nothing
    section("Step 5 — Attacker Intercepts the Transfer")

    intercepted_sample = encrypted_payload[:80].hex()
    attacker_sees(
        f"Intercepted data ({len(encrypted_payload)} bytes):\n"
        f"{intercepted_sample}...\n\n"
        f"[ATTACKER CANNOT DECRYPT — no private keys, no shared secret]"
    )

    fail("Attacker has the encrypted data — completely unreadable")
    fail("Without both private keys, decryption is mathematically impossible")
    fail("Breaking AES-256-GCM by brute force: longer than age of universe")
    divider()

    # ── Step 6: Provider B decrypts successfully
    section("Step 6 — Provider B Decrypts Successfully")

    hkdf_b = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"CXP-credential-transfer-v1"
    )
    encryption_key_b = hkdf_b.derive(shared_secret_b)
    aesgcm_b         = AESGCM(encryption_key_b)
    decrypted_payload = aesgcm_b.decrypt(nonce, encrypted_payload, None)
    decrypted_data    = json.loads(decrypted_payload)

    success("Provider B decrypted credentials successfully")
    success(f"All {len(decrypted_data['credentials'])} credentials received intact")
    print()
    for cred in decrypted_data["credentials"]:
        print(f"  {GREEN}✔  {cred['user']:<30} transferred safely{RESET}")

    return encrypted_payload


# ════════════════════════════════════════════════════════════
#  ACT 3 — SIDE BY SIDE COMPARISON
# ════════════════════════════════════════════════════════════

def act_three_comparison():
    banner("ACT 3 — SIDE BY SIDE COMPARISON", CYAN)

    categories = [
        ("Format",               "Plain text CSV",             "AES-256-GCM encrypted"),
        ("Encryption",           "None",                       "Real X25519 + AES-256-GCM"),
        ("Key Exchange",         "None",                       "Diffie-Hellman (X25519)"),
        ("Secret transmitted?",  "Password in plain text",     "Nothing — derived locally"),
        ("Attacker success rate","100% — reads everything",    "0% — sees only gibberish"),
        ("Skill to attack",      "None — open the file",       "Break AES-256 (impossible)"),
        ("Standard",             "No standard — chaotic",      "FIDO Alliance CXF/CXP"),
        ("Provider compatibility","Broken — different formats", "Universal — one standard"),
    ]

    col1 = 26
    col2 = 28
    col3 = 28

    print(f"  {BOLD}{'Category':<{col1}}{'CSV Export':<{col2}}{'CXP Transfer':<{col3}}{RESET}")
    print(f"  {'─' * col1}{'─' * col2}{'─' * col3}")

    for cat, csv_val, cxp_val in categories:
        print(f"  {WHITE}{cat:<{col1}}{RED}{csv_val:<{col2}}{GREEN}{cxp_val:<{col3}}{RESET}")

    print()
    divider()

    # Final verdict
    print(f"  {BOLD}{CYAN}CONCLUSION{RESET}\n")
    print(f"  {WHITE}The CSV method exposes every credential the moment")
    print(f"  the file is created. There is no technical barrier")
    print(f"  between an attacker and your passwords — just a file.")
    print()
    print(f"  CXP uses real cryptography — X25519 Diffie-Hellman")
    print(f"  key exchange ensures the encryption key never travels")
    print(f"  across the network. AES-256-GCM makes the payload")
    print(f"  unreadable to anyone without the private keys.")
    print()
    print(f"  This is why the FIDO Alliance published CXP in 2025.")
    print(f"  This is why Apple implemented it in iOS 26.")
    print(f"  This is the gap that needs to close — globally.{RESET}")
    print()

    banner("DEMO COMPLETE — ZEROKEY PROJECT | 2026", CYAN)
    print(f"  {DIM}Built by Koushik | github.com/[KoushikGollamudi]{RESET}\n")


# ════════════════════════════════════════════════════════════
#  MAIN — RUN ALL THREE ACTS
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    banner("CSV vs CXP SECURE TRANSFER DEMO", CYAN)
    print(f"  {WHITE}This demo uses REAL cryptography:{RESET}")
    print(f"  {DIM}  ● X25519 Diffie-Hellman key exchange{RESET}")
    print(f"  {DIM}  ● HKDF-SHA256 key derivation{RESET}")
    print(f"  {DIM}  ● AES-256-GCM authenticated encryption{RESET}")
    print(f"  {DIM}  ● FIDO Alliance CXF payload format{RESET}")
    print()

    act_one_csv()
    act_two_cxp()
    act_three_comparison()
