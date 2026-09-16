# -*- coding: utf-8 -*-
from __future__ import annotations

import atexit
import base64
import hashlib
import hmac
import marshal
import os
import shutil
import signal
import sys
import time
import zlib
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
except ImportError:
    print("[SECURITY] Missing dependency: cryptography", file=sys.stderr)
    raise SystemExit(1)

ESC = "\033["
RESET = f"{ESC}0m"
RED = f"{ESC}91m"
YELLOW = f"{ESC}93m"

FORMAT_VERSION = 6
AAD = base64.b64decode('UFktUFJPVEVDVE9SLzYvQ0hBQ0hBMjAtUE9MWTEzMDUvTUFSU0hBTA==')
KEY = base64.b64decode('DfWjM6d35nAFvbWMx+Y91aJaYZlvaKt00dsAfm+UzGU=')
NONCE = base64.b64decode('zbRebIxsRHkbX7Pm')
PAYLOAD = base64.b64decode('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')
EXPECTED_PAYLOAD_SHA256 = '07ff04025f2223f814aa32037adcaf0f30c39d19d059cc8b9d36361f0a1a7e13'
EXPECTED_LOADER_SHA256 = '8088046655c27bb1e525dc455ed50f272000a4161a11f2ea567ca077beadbd8b'
ORIGINAL_NAME = 'spamban.py'
ORIGINAL_ABS_PATH = '/storage/emulated/0/termux/valez/tools/spamban.py'
BUILD_PYTHON = (3, 14)
BUILD_IMPLEMENTATION = 'cpython'
BUILD_CACHE_TAG = 'cpython-314'

RUNTIME_ROOT = Path.home() / ".cache" / "py_protector"
RUNTIME_DIR = None
CLEANED = False


def cleanup():
    global CLEANED
    if CLEANED:
        return
    CLEANED = True
    if RUNTIME_DIR is not None:
        try:
            shutil.rmtree(RUNTIME_DIR, ignore_errors=True)
        except Exception:
            pass


def fail(reason: str):
    print(f"{RED}{reason}{RESET}", file=sys.stderr)
    cleanup()
    raise SystemExit(1)


def security_event(reason: str):
    try:
        RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
        log = RUNTIME_ROOT / "security.log"
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"[{stamp}] {reason}\n")
        try:
            log.chmod(0o600)
        except Exception:
            pass
    except Exception:
        pass


def signal_handler(signum, frame):
    cleanup()
    raise SystemExit(128 + int(signum))


def install_cleanup():
    atexit.register(cleanup)
    for name in ("SIGINT", "SIGTERM", "SIGHUP"):
        sig = getattr(signal, name, None)
        if sig is not None:
            try:
                signal.signal(sig, signal_handler)
            except Exception:
                pass


def verify_runtime():
    # The loader itself is .py, so this check produces a clear message instead
    # of Python failing first with "bad magic number".
    if sys.implementation.name != BUILD_IMPLEMENTATION:
        security_event("INTERPRETER_MISMATCH")
        fail("[!] Python implementation mismatch.")

    if sys.version_info[:2] != BUILD_PYTHON:
        security_event("PYTHON_VERSION_MISMATCH")
        fail(
            "[!] Unsupported Python version. "
            f"Required {BUILD_PYTHON[0]}.{BUILD_PYTHON[1]}, "
            f"running {sys.version_info[0]}.{sys.version_info[1]}."
        )

    cache_tag = getattr(sys.implementation, "cache_tag", "") or ""
    if cache_tag != BUILD_CACHE_TAG:
        security_event("CACHE_TAG_MISMATCH")
        fail("[!] Python cache tag mismatch.")


def create_runtime():
    global RUNTIME_DIR
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    runtime_name = f"session_{os.getpid()}_{os.urandom(8).hex()}"
    RUNTIME_DIR = RUNTIME_ROOT / runtime_name
    RUNTIME_DIR.mkdir(mode=0o700)


def verify_file_identity():
    # The output loader is intentionally relocatable. We do not require a fixed
    # absolute path because that would make copying a valid file fail.
    if Path(__file__).name != Path(EXPECTED_LOADER_NAME).name:
        security_event("LOADER_RENAME_DETECTED")
        fail("[!] Protected filename mismatch.")


def verify_payload():
    actual = hashlib.sha256(PAYLOAD).hexdigest()
    if not hmac.compare_digest(actual, EXPECTED_PAYLOAD_SHA256):
        security_event("PAYLOAD_INTEGRITY_FAILURE")
        fail("[!] Payload integrity check failed.")


def decrypt_bytecode():
    try:
        compressed = ChaCha20Poly1305(KEY).decrypt(
            NONCE,
            PAYLOAD,
            AAD,
        )
        raw = zlib.decompress(compressed)
        return raw
    except Exception:
        security_event("DECRYPTION_FAILURE")
        fail("[!] Payload decryption failed.")


def execute():
    raw = decrypt_bytecode()
    try:
        code = marshal.loads(raw)
    except Exception:
        security_event("INVALID_BYTECODE")
        fail("[!] Invalid bytecode payload.")

    # Make imports next to the protected script behave naturally.
    script_dir = str(Path(__file__).resolve().parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    namespace = {
        "__name__": "__main__",
        "__package__": None,
        "__cached__": None,
        "__loader__": None,
        "__spec__": None,
        "__file__": str(Path(__file__).resolve()),
        "__builtins__": __builtins__,
    }

    try:
        exec(code, namespace, namespace)
    except KeyboardInterrupt:
        raise
    except SystemExit:
        raise


EXPECTED_LOADER_NAME = 'spamban.py'


def main():
    install_cleanup()
    try:
        verify_runtime()
        create_runtime()
        verify_file_identity()
        verify_payload()
        execute()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
