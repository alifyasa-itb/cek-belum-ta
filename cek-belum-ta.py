#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fire",
#     "requests",
#     "tqdm",
# ]
# ///

import json
import urllib.request
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import cast, override

from fire import Fire
from requests import Session
from tqdm import tqdm


class StudentDataRepository(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.initialize()

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def get_name_from_nim(self, nim: str) -> str | None:
        pass

    @abstractmethod
    def get_nim_with_prefix(self, nim_prefix: str) -> list[str]:
        pass


class MKAmadeusStudentDataRepository(StudentDataRepository):
    STUDENT_DATA_PATH: Path = Path.cwd() / "data" / "data_13_22.json"
    STUDENT_DATA_URL: str = "https://raw.githubusercontent.com/mkamadeus/geprek-nim-finder/refs/heads/main/src/json/data_13_22.json"

    STUDENT_DATA: dict[str, str] = {}

    @override
    def initialize(self) -> None:
        super().initialize()
        self.get_student_data()

    @override
    def get_name_from_nim(self, nim: str) -> str | None:
        return self.STUDENT_DATA.get(nim)

    @override
    def get_nim_with_prefix(self, nim_prefix: str) -> list[str]:
        matching_nims: list[str] = []
        for nim in self.STUDENT_DATA:
            if nim.startswith(nim_prefix):
                matching_nims.append(nim)
        return matching_nims

    def download_student_data(self) -> None:
        self.STUDENT_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        print(f"Mencoba Download Data Mahasiswa dari {self.STUDENT_DATA_URL}")
        _ = urllib.request.urlretrieve(self.STUDENT_DATA_URL, self.STUDENT_DATA_PATH)

    def get_student_data(self):
        if not self.STUDENT_DATA_PATH.exists():
            self.download_student_data()

        with self.STUDENT_DATA_PATH.open("r", encoding="utf-8") as f:
            data = cast(list[list[str]], json.load(f))

        for row in data:
            name = row[0]
            nim_tpb = row[1]

            self.STUDENT_DATA[nim_tpb] = name

            if len(row) >= 3:
                nim_jurusan = row[2]
                self.STUDENT_DATA[nim_jurusan] = name


class TAStatusChecker(ABC):
    session: Session = Session()
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self) -> None:
        self.session.headers.update(self.headers)
        super().__init__()

    @abstractmethod
    def check_status_for_nim(self, nim: str) -> bool:
        pass


class DigilibTAStatusChecker(TAStatusChecker):
    endpoint: str = "https://digilib.itb.ac.id/gdl/go/{}"

    @override
    def check_status_for_nim(self, nim: str) -> bool:
        url = self.endpoint.format(nim)
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        text = resp.text
        return "Hasil Pencarian: 1" in text


def main(kode_jurusan: str = "135", angkatan: str = "20") -> None:
    angkatan = str(angkatan).zfill(2)

    print(f"Mencari yang belum selesai TA dari {kode_jurusan}{angkatan}XXX")

    now = datetime.now().astimezone().strftime("%a, %d %b %Y %H:%M:%S %z")
    print(f"Time: {now}")

    student_data_repository = MKAmadeusStudentDataRepository()
    ta_status_checker = DigilibTAStatusChecker()

    daftar_nim = sorted(
        student_data_repository.get_nim_with_prefix(f"{kode_jurusan}{angkatan}")
    )

    def check_one_nim(nim: str):
        ta_submitted = ta_status_checker.check_status_for_nim(nim)
        if not ta_submitted:
            return nim, student_data_repository.get_name_from_nim(nim)
        return None

    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_one_nim, nim): nim for nim in daftar_nim}

        for future in tqdm(as_completed(futures), total=len(futures)):
            result = future.result()  # raises if HTTP error
            if result is None:
                continue

            nim = result[0]
            nama = result[1]
            if nama is None:
                continue
            results[nim] = nama

    for nim in sorted(results):
        print(nim, results[nim])
    print(f"Total:   {len(results)} Mahasiswa")


if __name__ == "__main__":
    Fire(main)
