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
KEY = base64.b64decode('6CxL2h7/b4go77iKDgwf8SLaAdfdkvgrh1SWPC8Y6PU=')
NONCE = base64.b64decode('W2cmpEHi8g61JVzv')
PAYLOAD = base64.b64decode('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')
EXPECTED_PAYLOAD_SHA256 = '4e4e838438313db434e832faa8f07b51fa15e2b72c7548a12e44883f93bc72a7'
EXPECTED_LOADER_SHA256 = 'bce58f28482ff9200974d54f6396b3c17ff9e39c5cb305c1c7ee0b1263e66af2'
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
