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
KEY = base64.b64decode('WsBaUO/os0RT+FV/HXovJekSB/nycaF14RiqTXQSZBA=')
NONCE = base64.b64decode('4kgPvRL6R31XyEaJ')
PAYLOAD = base64.b64decode('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')
EXPECTED_PAYLOAD_SHA256 = 'd14204f2ccdf357e90806afb9b8d98a6da8e65695e46be35beb0175cd126ec54'
EXPECTED_LOADER_SHA256 = 'c9e8d4ab1723b22769759fff7eceb6d39930a763ee4f39f6ee0f5a30e1656958'
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
