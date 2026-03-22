# CSV vs CXP Secure Transfer Demo

A Python demonstration showing exactly why the current CSV 
credential export method is dangerously insecure — and how 
the FIDO Alliance's Credential Exchange Protocol (CXP) solves 
it using real cryptography.

## What This Demo Shows
- **Act 1:** CSV export — attacker reads everything instantly
- **Act 2:** CXP transfer — real X25519 Diffie-Hellman + AES-256-GCM
- **Act 3:** Side by side comparison

## Cryptography Used
- X25519 Diffie-Hellman key exchange
- HKDF-SHA256 key derivation  
- AES-256-GCM authenticated encryption
- FIDO Alliance CXF payload format

## How To Run
1. Open [Google Colab](https://colab.research.google.com)
2. Create a new notebook
3. Paste the entire `csv_vs_cxp_demo.py` file into one cell
4. Run — no installation needed

## Part of ZeroKey Project
This demo is the foundation of ZeroKey — a research initiative 
to design a cryptographic account recovery protocol that works 
with zero prior setup, solving the last remaining problem in 
passwordless authentication.

