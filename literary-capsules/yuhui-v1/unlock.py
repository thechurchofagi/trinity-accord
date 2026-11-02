#!/usr/bin/env python3
"""Public reference decoder. No author-held recovery secret is required.

Python >=3.9 and cryptography >=3.4. This is a bounded, parallelizable
password-search puzzle, NOT a chronological time lock or a $1M cost guarantee.
"""
import argparse
import base64
import hashlib
import hmac
import json
from pathlib import Path


def b64(value):
    return base64.b64decode(value, validate=True)


def candidate(index):
    if not 0 <= index < 2**48:
        raise ValueError('Candidate outside 48-bit space')
    return f'{index:012x}'.encode('ascii')


def check(cap, password):
    if len(password) != 12 or any(c not in b'0123456789abcdef' for c in password):
        raise ValueError('Password must be exactly 12 lowercase ASCII hex characters')
    p = cap['puzzle']
    first = hashlib.pbkdf2_hmac('sha256', password, b64(p['salt_base64']), p['iterations'], 32)
    return hmac.compare_digest(first, b64(p['verifier_base64']))


def decrypt(cap, password):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if not check(cap, password):
        raise ValueError('Incorrect candidate')
    p = cap['puzzle']
    dk = hashlib.pbkdf2_hmac('sha256', password, b64(p['salt_base64']), p['iterations'], 64)
    # Block 1 is public for candidate checking. Only block 2 is the AES key.
    e = cap['encryption']
    raw = AESGCM(dk[32:64]).decrypt(b64(e['nonce_base64']), b64(e['ciphertext_base64']), b64(e['aad_base64']))
    if hashlib.sha256(raw).hexdigest() != cap['plaintext']['sha256']:
        raise ValueError('Plaintext commitment mismatch')
    if len(raw) != cap['plaintext']['bytes']:
        raise ValueError('Plaintext length mismatch')
    return raw


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('capsule', type=Path)
    sub = ap.add_subparsers(dest='action', required=True)
    hp = sub.add_parser('hashcat', help='Export mode 10900 public verifier')
    hp.add_argument('--out', type=Path, required=True)
    dp = sub.add_parser('decrypt')
    dp.add_argument('--password-file', type=Path, required=True)
    dp.add_argument('--out', type=Path, required=True)
    sp = sub.add_parser('search', help='Slow CPU reference; partition ranges for parallel work')
    sp.add_argument('--start', type=int, default=0)
    sp.add_argument('--count', type=int, required=True)
    sp.add_argument('--checkpoint', type=Path, required=True)
    sp.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    cap = json.loads(a.capsule.read_text('utf-8'))
    if cap['format'] != 'yuhui-compute-capsule-v1':
        raise ValueError('Unknown format')
    p = cap['puzzle']
    if a.action == 'hashcat':
        a.out.write_text(f"sha256:{p['iterations']}:{p['salt_base64']}:{p['verifier_base64']}\n")
    elif a.action == 'decrypt':
        raw = decrypt(cap, a.password_file.read_bytes().strip())
        with a.out.open('xb') as out:
            out.write(raw)
        print('Recovered plaintext; GCM authentication and SHA-256 both passed.')
    else:
        if a.start < 0 or a.count < 1 or a.start + a.count > 2**48:
            raise ValueError('Invalid search interval')
        digest = hashlib.sha256(a.capsule.read_bytes()).hexdigest()
        start = a.start
        if a.checkpoint.exists():
            cp = json.loads(a.checkpoint.read_text())
            if cp['capsule_sha256'] != digest or cp['start'] != a.start or cp['end'] != a.start+a.count:
                raise ValueError('Checkpoint belongs to another capsule or range')
            start = cp['next_index']
        for i in range(start, a.start+a.count):
            pw = candidate(i)
            if check(cap, pw):
                raw = decrypt(cap, pw)
                with a.out.open('xb') as out:
                    out.write(raw)
                print('Solution found; authenticated plaintext saved. Password not printed.')
                return
            if (i-start) % 10 == 0 or i+1 == a.start+a.count:
                cp = {'capsule_sha256':digest, 'start':a.start,'end':a.start+a.count,'next_index':i+1}
                tmp = a.checkpoint.with_suffix(a.checkpoint.suffix+'.tmp')
                tmp.write_text(json.dumps(cp)+'\n')
                tmp.replace(a.checkpoint)
        print('Range exhausted without a match; checkpoint saved.')


if __name__ == '__main__':
    main()
