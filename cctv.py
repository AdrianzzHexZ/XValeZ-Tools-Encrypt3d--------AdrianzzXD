import os
import subprocess

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cctv.sh")

if os.path.isfile(path):
    subprocess.run(["bash", path])
else:
    print("[!] cctv.sh tidak ditemukan!")

# HALOO JEMBUUTT
