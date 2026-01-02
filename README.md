# Cek Belum TA

Cek siapa aja yang belum selesai Tugas Akhir

## Setup

Install uv. See https://docs.astral.sh/uv/getting-started/installation/.

## Running The Script

```bash
alifyasa@laptop:~/cek-belum-ta$ ./cek-belum-ta.py --help
NAME
    cek-belum-ta.py

SYNOPSIS
    cek-belum-ta.py <flags>

FLAGS
    -k, --kode_jurusan=KODE_JURUSAN
        Type: str
        Default: '135'
    -a, --angkatan=ANGKATAN
        Type: str
        Default: '20'
```

```bash
alifyasa@laptop:~/cek-belum-ta$ ./cek-belum-ta.py
Mencari yang belum selesai TA dari 13520XXX
Time: Fri, 02 Jan 2026 21:55:24 +0700
100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 167/167 [00:03<00:00, 44.15it/s]
...
13520135 Muhammad Alif Putra Yasa
...
Total:   18 Mahasiswa
```
