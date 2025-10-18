import os
import numpy as np


def generate_naca_4_digit_airfoil(m, p, t, num_points=50):
    m = m / 100.0
    p = p / 10.0
    t = t / 100.0

    beta = np.linspace(0, np.pi, num_points)
    x = 0.5 * (1 - np.cos(beta))

    yt = (t / 0.2) * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    for i in range(len(x)):
        if x[i] < p:
            yc[i] = (m / p ** 2) * (2 * p * x[i] - x[i] ** 2)
            dyc_dx[i] = (2 * m / p ** 2) * (p - x[i])
        else:
            yc[i] = (m / (1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x[i] - x[i] ** 2)
            dyc_dx[i] = (2 * m / (1 - p) ** 2) * (p - x[i])

    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    x_coords = np.concatenate([xu[::-1], xl[1:]])
    y_coords = np.concatenate([yu[::-1], yl[1:]])

    return x_coords, y_coords


def generate_naca_5_digit_airfoil(l, p, q, t, num_points=50):
    t = t / 100.0

    beta = np.linspace(0, np.pi, num_points)
    x = 0.5 * (1 - np.cos(beta))

    yt = (t / 0.2) * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)

    r = 1.1019 * (l * 1.5 / 2) ** 2

    if q == 0:
        if p == 2:
            k1 = 15.793
            m = 0.2025
        elif p == 3:
            k1 = 15.957
            m = 0.30
        elif p == 4:
            k1 = 16.161
            m = 0.405
        elif p == 5:
            k1 = 16.200
            m = 0.50
    else:
        if p == 2:
            k1 = 12.0
            m = 0.20
        elif p == 3:
            k1 = 13.0
            m = 0.30
        elif p == 4:
            k1 = 14.0
            m = 0.40
        elif p == 5:
            k1 = 15.0
            m = 0.50

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    for i in range(len(x)):
        if x[i] < m:
            yc[i] = (k1 / 6) * (x[i] ** 3 - 3 * m * x[i] ** 2 + m ** 2 * (3 - m) * x[i])
            dyc_dx[i] = (k1 / 6) * (3 * x[i] ** 2 - 6 * m * x[i] + m ** 2 * (3 - m))
        else:
            yc[i] = (k1 / 6) * m ** 3 * (1 - x[i])
            dyc_dx[i] = -(k1 / 6) * m ** 3

    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    x_coords = np.concatenate([xu[::-1], xl[1:]])
    y_coords = np.concatenate([yu[::-1], yl[1:]])

    return x_coords, y_coords


def save_airfoil_data(filename, x, y, airfoil_name):
    with open(filename, 'w') as f:
        f.write(f"{airfoil_name}\n")
        for xi, yi in zip(x, y):
            f.write(f"{xi:.4f}     {yi:.4f}\n")


def main():
    os.makedirs('airfoil_data', exist_ok=True)

    np.random.seed(42)

    for i in range(1000):
        if np.random.random() < 0.7:
            m = np.random.choice([0, 1, 2, 3, 4, 5, 6])
            p = np.random.choice([2, 3, 4, 5, 6])
            t = np.random.choice([6, 8, 9, 10, 12, 14, 15, 18, 21, 24])

            airfoil_name = f"NACA {m}{p}{t:02d}"
            x, y = generate_naca_4_digit_airfoil(m, p, t)

        else:
            l = np.random.choice([2, 3, 4])
            p = np.random.choice([2, 3, 4, 5])
            q = np.random.choice([0, 1])
            t = np.random.choice([8, 10, 12, 15, 18, 21])

            airfoil_name = f"NACA {l}{p}{q}{t:02d}"
            x, y = generate_naca_5_digit_airfoil(l, p, q, t)

        filename = f"airfoil_data/airfoil_{i + 1:04d}.dat"
        save_airfoil_data(filename, x, y, airfoil_name)

        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} airfoil data files")

    print("All 1000 airfoil data files have been generated!")


if __name__ == "__main__":
    main()
