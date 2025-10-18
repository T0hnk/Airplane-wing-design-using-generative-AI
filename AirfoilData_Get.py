import requests
import os
import time
import random
from urllib.parse import urljoin
import re
import traceback

def download_all_airfoils(base_url, output_dir="all_airfoils"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created airfoil data directory: {output_dir}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        print(f"Fetching main page: {base_url}")
        response = session.get(base_url, timeout=30)
        response.raise_for_status()
        print("Main page fetched successfully!")

        dat_links = re.findall(r'href="(coord/[^"]+\.dat)"', response.text, re.IGNORECASE)

        if not dat_links:
            print("No airfoil data links found, please check the page structure")
            return

        unique_links = list(set(dat_links))
        print(f"Found {len(unique_links)} unique airfoil data links")

        downloaded_count = 0
        error_count = 0
        skipped_count = 0

        random.shuffle(unique_links)

        print("Starting airfoil data file downloads...")

        for i, rel_path in enumerate(unique_links):
            file_url = urljoin(base_url, rel_path)

            filename = os.path.basename(rel_path)
            local_path = os.path.join(output_dir, filename)

            if os.path.exists(local_path):
                print(f"[{i + 1}/{len(unique_links)}] Already exists, skipping: {filename}")
                skipped_count += 1
                continue

            print(f"[{i + 1}/{len(unique_links)}] Attempting to download: {filename}")

            try:
                delay = random.uniform(1, 3)
                time.sleep(delay)

                file_response = session.get(file_url, timeout=30)
                file_response.raise_for_status()

                content = file_response.content
                if len(content) < 50:
                    print(f"  File content too small ({len(content)} bytes), likely invalid, skipping")
                    error_count += 1
                    continue

                with open(local_path, 'wb') as f:
                    f.write(content)

                downloaded_count += 1
                print(f"  Successfully downloaded: {filename} (Size: {len(content)} bytes)")

            except requests.exceptions.RequestException as e:
                error_count += 1
                print(f"  Download failed: {str(e)}")
            except Exception as e:
                error_count += 1
                print(f"  Unknown error: {str(e)}")
                traceback.print_exc()

        print(f"\nAll airfoil data downloads completed!")
        print(f"Successfully downloaded: {downloaded_count} files")
        print(f"Skipped (already exists): {skipped_count} files")
        print(f"Failed: {error_count} files")
        print(f"Total processed: {len(unique_links)} airfoils")

    except requests.exceptions.RequestException as e:
        print(f"Network request error: {str(e)}")
    except Exception as e:
        print(f"Unknown error occurred: {str(e)}")
        traceback.print_exc()


def validate_downloaded_files(directory="all_airfoils"):
    print(f"\nValidating files in {directory} directory...")

    if not os.path.exists(directory):
        print("Directory does not exist")
        return

    dat_files = [f for f in os.listdir(directory) if f.endswith('.dat')]

    if not dat_files:
        print("No .dat files found")
        return

    print(f"Found {len(dat_files)} .dat files")

    size_stats = {}
    for filename in dat_files:
        try:
            size = os.path.getsize(os.path.join(directory, filename))
            size_range = f"{(size // 500) * 500}-{(size // 500) * 500 + 499} bytes"
            size_stats[size_range] = size_stats.get(size_range, 0) + 1
        except OSError:
            pass

    print("\nFile size distribution:")
    for size_range, count in sorted(size_stats.items()):
        print(f"  {size_range}: {count} files")
    print("\nRandom sample files (first 10):")
    sample_files = random.sample(dat_files, min(10, len(dat_files)))
    for i, filename in enumerate(sample_files):
        file_path = os.path.join(directory, filename)
        try:
            size = os.path.getsize(file_path)
            print(f"  {i + 1}. {filename} ({size} bytes)")
        except OSError:
            print(f"  {i + 1}. {filename} (Failed to get size)")

if __name__ == "__main__":
    base_url = "https://m-selig.ae.illinois.edu/ads/coord_database.html"
    download_all_airfoils(base_url)
    validate_downloaded_files()
