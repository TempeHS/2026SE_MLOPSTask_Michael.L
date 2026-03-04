import os
import csv
import zipfile
import urllib.request
from pathlib import Path

URL = "https://assets.worldcubeassociation.org/export/results/WCA_export_v2_062_20260303T000006Z.tsv.zip"
DOWNLOAD_DIR = Path("wca_export")
CSV_DIR = DOWNLOAD_DIR / "csv"


def progress_hook(block_count: int, block_size: int, total_size: int) -> None:
    downloaded = block_count * block_size
    if total_size > 0:
        pct = min(downloaded / total_size * 100, 100)
        bar = "█" * int(pct // 2) + "░" * (50 - int(pct // 2))
        mb_done = downloaded / 1_048_576
        mb_total = total_size / 1_048_576
        print(
            f"\r  [{bar}] {pct:5.1f}%  {mb_done:.1f}/{mb_total:.1f} MB",
            end="",
            flush=True,
        )
    else:
        print(f"\r  Downloaded {downloaded / 1_048_576:.1f} MB", end="", flush=True)


def download(url: str, dest: Path) -> Path:
    filename = dest / url.split("/")[-1]
    if filename.exists():
        print(f"  ✔ Already downloaded: {filename.name} — skipping.")
        return filename
    dest.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading {url.split('/')[-1]} …")
    urllib.request.urlretrieve(url, filename, reporthook=progress_hook)
    print()  # newline after progress bar
    print(f"  ✔ Saved to {filename}")
    return filename


def unzip(zip_path: Path, extract_to: Path) -> list[Path]:
    extract_to.mkdir(parents=True, exist_ok=True)
    tsv_files = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        members = [m for m in zf.namelist() if m.endswith(".tsv")]
        total = len(members)
        print(f"  Found {total} TSV file(s) in archive.")
        for i, member in enumerate(members, 1):
            out_path = extract_to / Path(member).name
            if not out_path.exists():
                with zf.open(member) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())
                print(f"  [{i:>3}/{total}] Extracted {Path(member).name}")
            else:
                print(
                    f"  [{i:>3}/{total}] Already exists, skipping {Path(member).name}"
                )
            tsv_files.append(out_path)
    return tsv_files


def tsv_to_csv(tsv_path: Path, csv_path: Path) -> int:
    """Convert a single TSV file to CSV. Returns the row count."""
    row_count = 0
    with (
        open(tsv_path, "r", encoding="utf-8", newline="") as tsv_f,
        open(csv_path, "w", encoding="utf-8", newline="") as csv_f,
    ):
        reader = csv.reader(tsv_f, delimiter="\t")
        writer = csv.writer(csv_f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            writer.writerow(row)
            row_count += 1
    return row_count


def convert_all(tsv_files: list[Path], csv_dir: Path) -> None:
    csv_dir.mkdir(parents=True, exist_ok=True)
    total = len(tsv_files)
    for i, tsv_path in enumerate(tsv_files, 1):
        csv_path = csv_dir / tsv_path.with_suffix(".csv").name
        if csv_path.exists():
            print(f"  [{i:>3}/{total}] Already converted, skipping {tsv_path.name}")
            continue
        rows = tsv_to_csv(tsv_path, csv_path)
        print(
            f"  [{i:>3}/{total}] {tsv_path.name:50s} → {csv_path.name}  ({rows:,} rows)"
        )


def main() -> None:
    print("=" * 60)
    print("  WCA Export Downloader & TSV → CSV Converter")
    print("=" * 60)

    print("\n[1/3] Downloading …")
    zip_path = download(URL, DOWNLOAD_DIR)

    print("\n[2/3] Unzipping …")
    tsv_files = unzip(zip_path, DOWNLOAD_DIR)

    print("\n[3/3] Converting TSV → CSV …")
    convert_all(tsv_files, CSV_DIR)

    print("\n" + "=" * 60)
    print(f"  Done! CSV files are in: {CSV_DIR.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
