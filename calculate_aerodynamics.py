import os
import subprocess
import pandas as pd
import time
import numpy as np
import shutil
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

xfoil_path = r"E:\Downloads\XFOIL6.99\xfoil.exe"
airfoil_folder = "airfoil_data"
result_folder = "xfoil_results"
strange_folder = "strange_data"
output_csv = "xfoil_data.csv"

re = 1e6
mach = 0.15
alpha_start = -5
alpha_end = 15
alpha_step = 1

os.makedirs(result_folder, exist_ok=True)
os.makedirs(strange_folder, exist_ok=True)


def is_abnormal(df):
    if df.empty:
        return True
    if df.isnull().values.any():
        return True
    if (df["CD"] <= 0).any():
        return True
    if df["CL"].abs().sum() == 0 or df["CD"].abs().sum() == 0:
        return True
    if (df["CL"] / df["CD"]).abs().max() > 500:
        return True
    return False


def process_airfoil(file):
    if not file.lower().endswith(".dat"):
        return None

    airfoil_path = os.path.join(airfoil_folder, file)
    airfoil_name = os.path.splitext(file)[0]
    polar_file = os.path.join(result_folder, f"{airfoil_name}_polar.txt")

    temp_inp = f"temp_{airfoil_name}.inp"

    commands = f"""
LOAD {airfoil_path}
PANE
OPER
VISC {re}
MACH {mach}
ITER 200
PACC
{polar_file}

ASEQ {alpha_start} {alpha_end} {alpha_step}
PACC
QUIT
"""

    with open(temp_inp, "w") as f:
        f.write(commands)

    try:
        subprocess.run(
            [xfoil_path],
            input=open(temp_inp).read(),
            text=True,
            capture_output=True,
            timeout=10
        )
    except subprocess.TimeoutExpired:
        print(f"Timeout {airfoil_name}")
        strange_path = os.path.join(strange_folder, file)
        shutil.move(airfoil_path, strange_path)
        if os.path.exists(temp_inp):
            os.remove(temp_inp)
        return None
    except Exception as e:
        print(f"XFOIL error {airfoil_name}: {e}")
        strange_path = os.path.join(strange_folder, file)
        shutil.move(airfoil_path, strange_path)
        if os.path.exists(temp_inp):
            os.remove(temp_inp)
        return None

    if not os.path.exists(polar_file) or os.path.getsize(polar_file) < 200:
        print(f"No valid output {airfoil_name}")
        strange_path = os.path.join(strange_folder, file)
        shutil.move(airfoil_path, strange_path)
        if os.path.exists(temp_inp):
            os.remove(temp_inp)
        return None

    try:
        df = pd.read_csv(
            polar_file,
            sep=r"\s+",
            skiprows=12,
            names=["alpha", "CL", "CD", "CDp", "CM", "Top_Xtr", "Bot_Xtr"]
        )
    except Exception as e:
        print(f"Parse error {airfoil_name}: {e}")
        strange_path = os.path.join(strange_folder, file)
        shutil.move(airfoil_path, strange_path)
        if os.path.exists(temp_inp):
            os.remove(temp_inp)
        return None

    if is_abnormal(df):
        print(f"Abnormal data {airfoil_name}")
        strange_path = os.path.join(strange_folder, file)
        shutil.move(airfoil_path, strange_path)
        if os.path.exists(temp_inp):
            os.remove(temp_inp)
        return None

    df["Airfoil"] = airfoil_name
    df["CL/CD"] = df["CL"] / df["CD"]

    if os.path.exists(temp_inp):
        os.remove(temp_inp)

    print(f"Success {airfoil_name}")
    return df


def main():
    dat_files = [f for f in os.listdir(airfoil_folder) if f.lower().endswith(".dat")]

    print(f"Found {len(dat_files)} airfoil files")
    print("Starting parallel processing with 5 workers...")

    records = []

    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_airfoil, file): file for file in dat_files}

        for future in as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                if result is not None:
                    records.append(result)
            except Exception as e:
                print(f"Error processing {file}: {e}")

    if records:
        all_data = pd.concat(records, ignore_index=True)
        all_data.to_csv(output_csv, index=False)
        print(f"All results saved to {output_csv}")
        print(f"Valid airfoils: {len(records)}")
    else:
        print("No valid data generated")


if __name__ == "__main__":
    main()
