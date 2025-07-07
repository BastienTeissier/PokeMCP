import os
from pathlib import Path

from authlib.jose import JsonWebKey, jwk

# Use environment variable for key directory, fallback to local keys directory
_KEY_DIR = Path(os.environ.get("JWT_KEYS_DIR", "./keys"))
_KEY_DIR.mkdir(exist_ok=True)
_PRIVATE = _KEY_DIR / "jwt_private.pem"


def _load():
    """Load or generate RSA key pair for JWT signing."""
    if not _PRIVATE.exists():
        print("Generating new RSA key pair for JWT signing...")
        rsa = jwk.generate_key("RSA", 2048)
        _PRIVATE.write_bytes(rsa.as_pem(private=True))
        print(f"RSA key pair saved to {_PRIVATE}")
    return JsonWebKey.import_key(_PRIVATE.read_bytes())


# Global RSA key instance
RSA_KEY = _load()


def public_jwks():
    """Return public key in JWKS format."""
    return {"keys": [RSA_KEY.as_dict(is_private=False)]}
