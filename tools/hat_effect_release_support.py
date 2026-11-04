"""Scoped signed-release primitives shared by the HatEffect EXE upgrade.

No keys or full client backups are copied into the repository. The server's
existing Riftlock signer owns its key. This module has no standalone command.
"""
from pathlib import Path
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT.parent / 'BanquetOfHeroes'
ASSETS, SIGNATURE = 'riftlock-assets-v1.txt', 'riftlock-release.sig'
sys.path.insert(0, str(SERVER / 'tools'))
import riftlock_manifest as manifest
import riftlock_release as signing


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def closed(game):
    command = "$g='" + str(game).replace("'", "''") + "'; @(Get-Process | Where-Object { $_.Path -and (Split-Path -Parent $_.Path) -eq $g } | Select-Object Id,ProcessName) | ConvertTo-Json -Compress"
    result = subprocess.run(['powershell', '-NoProfile', '-Command', command],
                            capture_output=True, text=True, check=True, creationflags=0x08000000)
    assert not result.stdout.strip(), 'Close the game first: ' + result.stdout.strip()


def signature(exe, assets, sig, game):
    fields = dict(line.split('=', 1) for line in sig.read_text(encoding='ascii').splitlines())
    assert fields['format'] == 'riftlock-release-signature-v1'
    digest = manifest.release_digest(exe, game / 'riftlock.dll', game / 'libsodium.dll', assets)
    assert digest.hex() == fields['digest'], 'Signed digest does not match the files'
    public = bytes.fromhex(fields['public_key'])
    assert public in (game / 'riftlock.dll').read_bytes()
    statement = signing.release_statement(int(fields['build']), int(fields['release']), digest)
    sodium = manifest.load_sodium(SERVER / 'libsodium.dll')
    assert sodium.sodium_init() >= 0
    assert sodium.crypto_sign_verify_detached(
        (ctypes.c_ubyte * 64).from_buffer_copy(bytes.fromhex(fields['signature'])),
        (ctypes.c_ubyte * len(statement)).from_buffer_copy(statement),
        ctypes.c_ulonglong(len(statement)),
        (ctypes.c_ubyte * 32).from_buffer_copy(public)) == 0
    return dict(build=int(fields['build']), release=int(fields['release']),
                digest=digest.hex(), public_key=public.hex(), signature_verified=True)


def atomic_bytes(path, raw):
    temporary = path.with_name(path.name + '.hat77.pending')
    assert not temporary.exists(), 'Unexpected pending transaction: ' + str(temporary)
    try:
        temporary.write_bytes(raw)
        assert sha(temporary.read_bytes()) == sha(raw)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def fixture_at(work):
    fixture = work / 'fixture'
    fixture.mkdir()
    for name in ['Scripts', 'Patches']:
        shutil.copytree(ROOT / name, fixture / name, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ['Tables', 'Inputs', 'Languages', 'Styles', 'Images', 'win32']:
        os.symlink((ROOT / name).resolve(), fixture / name, target_is_directory=True)
    shutil.copy2(ROOT / 'Patches.yml', fixture / 'Patches.yml')
    (fixture / 'Assets').mkdir()
    if not (fixture / 'Patches/Premium.yml').exists():
        (fixture / 'Patches/Premium.yml').write_text('{}\n', encoding='utf-8')
    return fixture