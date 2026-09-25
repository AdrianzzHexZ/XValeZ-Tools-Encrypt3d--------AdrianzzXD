import os
import shutil
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JS_FILE = os.path.join(BASE_DIR, "pair_enc.js")
def main():
    if not os.path.isfile(JS_FILE):
        print(f"[ERROR] File tidak ditemukan: {JS_FILE}")
        sys.exit(1)
    node_path = shutil.which("node")
    if not node_path:
        for candidate in ("/usr/bin/node", "/usr/local/bin/node", "/opt/homebrew/bin/node"):
            if os.path.isfile(candidate):
                node_path = candidate
                break
    if not node_path:
        print("[ERROR] Node.js tidak ditemukan di PATH maupun lokasi umum.")
        print("Install Node.js dulu, atau set path manual di script ini.")
        sys.exit(1)
    os.system("clear")
    print(f"[INFO] Menjalankan: {node_path} {JS_FILE}\n")
    os.execv(node_path, [node_path, JS_FILE])
if __name__ == "__main__":
    main()
