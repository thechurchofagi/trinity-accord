#!/usr/bin/env python
# tools/ots-run.py
import os, sys, ctypes, ctypes.util

# 1) 指定 OpenSSL 1.1 DLL 搜索目录
os.add_dll_directory(r"C:\Program Files\OpenSSL-Win64\bin")

# 2) 预加载 libcrypto（BN_* 在这里）
try:
    _crypto = ctypes.cdll.LoadLibrary("libcrypto-1_1-x64.dll")
except Exception as e:
    print("FAIL to load libcrypto-1_1-x64.dll ->", e, file=sys.stderr)
    sys.exit(2)

# 可选：有则加载 libssl（不是必须）
try:
    _ssl = ctypes.cdll.LoadLibrary("libssl-1_1-x64.dll")
except Exception:
    _ssl = None

# 3) 修补 find_library：把 'ssl'/'crypto' 都指向 libcrypto-1_1-x64.dll
_orig_find = ctypes.util.find_library
def _patched_find(name: str):
    l = (name or "").lower()
    if l in ("ssl", "libssl", "crypto", "libcrypto", "libeay32"):
        return "libcrypto-1_1-x64.dll"
    return _orig_find(name)
ctypes.util.find_library = _patched_find

# 4) 进入 OTS 客户端入口
from otsclient.ots import main
if __name__ == "__main__":
    sys.exit(main())