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
        print(f"创建翼型数据目录: {output_dir}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        print(f"正在获取主页面: {base_url}")
        response = session.get(base_url, timeout=30)
        response.raise_for_status()
        print("主页面获取成功!")

        dat_links = re.findall(r'href="(coord/[^"]+\.dat)"', response.text, re.IGNORECASE)

        if not dat_links:
            print("未找到翼型数据链接，请检查页面结构")
            return

        unique_links = list(set(dat_links))
        print(f"找到 {len(unique_links)} 个唯一的翼型数据链接")

        downloaded_count = 0
        error_count = 0
        skipped_count = 0

        random.shuffle(unique_links)

        print("开始下载翼型数据文件...")

        for i, rel_path in enumerate(unique_links):
            file_url = urljoin(base_url, rel_path)

            filename = os.path.basename(rel_path)
            local_path = os.path.join(output_dir, filename)

            if os.path.exists(local_path):
                print(f"[{i + 1}/{len(unique_links)}] 已存在，跳过: {filename}")
                skipped_count += 1
                continue

            print(f"[{i + 1}/{len(unique_links)}] 尝试下载: {filename}")

            try:
                delay = random.uniform(1, 3)
                time.sleep(delay)

                file_response = session.get(file_url, timeout=30)
                file_response.raise_for_status()

                content = file_response.content
                if len(content) < 50:
                    print(f"  文件内容过小({len(content)}字节)，可能无效，跳过")
                    error_count += 1
                    continue

                with open(local_path, 'wb') as f:
                    f.write(content)

                downloaded_count += 1
                print(f"  成功下载: {filename} (大小: {len(content)} 字节)")

            except requests.exceptions.RequestException as e:
                error_count += 1
                print(f"  下载失败: {str(e)}")
            except Exception as e:
                error_count += 1
                print(f"  未知错误: {str(e)}")
                traceback.print_exc()

        print(f"\n所有翼型数据下载完成!")
        print(f"成功下载: {downloaded_count} 个文件")
        print(f"跳过已存在: {skipped_count} 个文件")
        print(f"失败: {error_count} 个文件")
        print(f"总计处理: {len(unique_links)} 个翼型")

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {str(e)}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        traceback.print_exc()


def validate_downloaded_files(directory="all_airfoils"):
    print(f"\n验证 {directory} 目录中的文件...")

    if not os.path.exists(directory):
        print("目录不存在")
        return

    dat_files = [f for f in os.listdir(directory) if f.endswith('.dat')]

    if not dat_files:
        print("未找到.dat文件")
        return

    print(f"找到 {len(dat_files)} 个.dat文件")

    size_stats = {}
    for filename in dat_files:
        try:
            size = os.path.getsize(os.path.join(directory, filename))
            size_range = f"{(size // 500) * 500}-{(size // 500) * 500 + 499}字节"
            size_stats[size_range] = size_stats.get(size_range, 0) + 1
        except OSError:
            pass

    print("\n文件大小分布:")
    for size_range, count in sorted(size_stats.items()):
        print(f"  {size_range}: {count}个文件")

    print("\n随机样本文件(前10个):")
    sample_files = random.sample(dat_files, min(10, len(dat_files)))
    for i, filename in enumerate(sample_files):
        file_path = os.path.join(directory, filename)
        try:
            size = os.path.getsize(file_path)
            print(f"  {i + 1}. {filename} ({size} 字节)")
        except OSError:
            print(f"  {i + 1}. {filename} (大小获取失败)")


if __name__ == "__main__":
    base_url = "https://m-selig.ae.illinois.edu/ads/coord_database.html"

    download_all_airfoils(base_url)

    validate_downloaded_files()

