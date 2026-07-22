import os
import sys
import json
import time
import logging
import argparse
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
import jwt

# Production-ready script to create/update a Generic Class & Object and generate save-to-wallet link.
# Requires: GOOGLE_WALLET_ISSUER_ID and GOOGLE_SERVICE_ACCOUNT_FILE env vars (or pass via args).
# Run in a venv with google-auth, requests, pyjwt installed.

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/wallet_object.issuer"]
PAYLOAD_TIMEOUT = 30

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_access_token(keyfile, scopes=DEFAULT_SCOPES):
    creds = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    return creds.token


def ensure_class(token, class_id, issuer_name="Issuer", program_name="Program", header_value="Carte"):
    url = "https://walletobjects.googleapis.com/walletobjects/v1/genericClass"
    payload = {
        "id": class_id,
        "issuerName": issuer_name,
        "programName": program_name,
        "genericClass": {
            "header": {"defaultValue": {"language": "fr-FR", "value": header_value}}
        }
    }
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, headers=h, json=payload, timeout=PAYLOAD_TIMEOUT)
    if r.status_code in (200, 201):
        logging.info("Class created.")
    elif r.status_code == 409:
        logging.info("Class already exists.")
    else:
        logging.error("Class creation failed: %s %s", r.status_code, r.text)
        r.raise_for_status()
    return r


def get_object(token, object_id):
    url = f"https://walletobjects.googleapis.com/walletobjects/v1/genericObject/{object_id}"
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=h, timeout=PAYLOAD_TIMEOUT)
    return r


def create_object(token, obj_payload):
    url = "https://walletobjects.googleapis.com/walletobjects/v1/genericObject"
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, headers=h, json=obj_payload, timeout=PAYLOAD_TIMEOUT)
    return r


def patch_object(token, object_id, obj_payload):
    url = f"https://walletobjects.googleapis.com/walletobjects/v1/genericObject/{object_id}"
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.patch(url, headers=h, json=obj_payload, timeout=PAYLOAD_TIMEOUT)
    return r


def generate_jwt_link(keyfile, object_id):
    with open(keyfile, "r") as f:
        j = json.load(f)
    private_key = j["private_key"]
    kid = j.get("private_key_id")
    iss = j["client_email"]
    iat = int(time.time())
    payload = {
        "iss": iss,
        "aud": "google",
        "origins": ["*"],
        "typ": "savetowallet",
        "iat": iat,
        "payload": {"genericObjects": [{"id": object_id}]}
    }
    headers = {"alg": "RS256", "kid": kid, "typ": "JWT"}
    token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return f"https://pay.google.com/gp/v/save/{token}"


def build_object_payload(issuer_id, object_id_suffix, class_id, title, header, text_modules):
    object_id = f"{issuer_id}.{object_id_suffix}"
    payload = {
        "id": object_id,
        "classId": class_id,
        "state": "ACTIVE",
        # fields at root (working format)
        "cardTitle": {"defaultValue": {"language": "fr-FR", "value": title}},
        "header": {"defaultValue": {"language": "fr-FR", "value": header}},
        "textModulesData": text_modules
    }
    return object_id, payload


def parse_args():
    p = argparse.ArgumentParser(description="Create/update Google Wallet generic class/object and print save link.")
    p.add_argument("--keyfile", default=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"), help="Service account JSON path")
    p.add_argument("--issuer", default=os.getenv("GOOGLE_WALLET_ISSUER_ID"), help="Issuer ID")
    p.add_argument("--class-id", help="Full class id (defaults to ISSUER.generic_class_prod)")
    p.add_argument("--object-suffix", default="generic_object_prod1", help="Suffix for object id (full id = ISSUER.suffix)")
    p.add_argument("--title", default="Carte Prod", help="Card title")
    p.add_argument("--header", default="Programme Prod", help="Header value")
    p.add_argument("--text", default="Informations", help="Text module body")
    p.add_argument("--create-class", action="store_true", help="Ensure class exists")
    p.add_argument("--force-update", action="store_true", help="Patch object if exists")
    return p.parse_args()


def main():
    args = parse_args()
    if not args.keyfile or not args.issuer:
        logging.error("Missing keyfile or issuer id. Set env or pass --keyfile and --issuer.")
        sys.exit(1)

    class_id = args.class_id or f"{args.issuer}.generic_class_prod"
    object_id_suffix = args.object_suffix

    try:
        token = get_access_token(args.keyfile)
    except Exception as e:
        logging.error("Failed to get access token: %s", e)
        sys.exit(1)

    if args.create_class:
        ensure_class(token, class_id, issuer_name="Yokalma", program_name="Yokalma Prod", header_value=args.header)

    object_id, obj_payload = build_object_payload(
        args.issuer, object_id_suffix, class_id, title=args.title,
        header=args.header, text_modules=[{"header": args.title, "body": args.text}]
    )

    # create or update
    r_get = get_object(token, object_id)
    if r_get.status_code == 200 and not args.force_update:
        logging.info("Object already exists; use --force-update to patch.")
    elif r_get.status_code == 200 and args.force_update:
        logging.info("Patching existing object...")
        r = patch_object(token, object_id, obj_payload)
        logging.info("Patch status: %s\n%s", r.status_code, r.text)
    else:
        logging.info("Creating object...")
        r = create_object(token, obj_payload)
        logging.info("Create status: %s\n%s", r.status_code, r.text)

    link = generate_jwt_link(args.keyfile, object_id)
    logging.info("Save-to-wallet link:\n%s", link)
    logging.info("Open link on device with admin/dev/test account for this issuer.")


if __name__ == "__main__":
    main()