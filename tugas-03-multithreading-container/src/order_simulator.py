"""Tugas 3 - Simulasi pesanan FoodGo dengan pekerja multithread."""

import argparse
import threading
import random
import time

NUM_ORDERS = 100        # jumlah pesanan simulasi yang masuk
NUM_WORKERS = 10        # jumlah thread pekerja

# Counter bersama untuk menghitung total pesanan yang berhasil diproses.
# Sengaja rawan race condition jika diakses tanpa proteksi.
processed_count = 0

lock = threading.Lock()


def process_order(order_id: int, use_lock: bool = True) -> None:
    """Proses satu pesanan. Dipanggil oleh tiap thread pekerja."""
    global processed_count

    # Simulasikan kerja yang dapat berjalan di luar bagian kritis.
    time.sleep(random.uniform(0.001, 0.01))

    if use_lock:
        with lock:
            processed_count += 1
    else:
        # Yield between the read and write to make the unsynchronized
        # read-modify-write race observable in this demonstration.
        current_count = processed_count
        time.sleep(0)
        processed_count = current_count + 1


def worker(order_ids: list[int], use_lock: bool = True) -> None:
    """Satu thread pekerja memproses sekumpulan order_id."""
    for order_id in order_ids:
        process_order(order_id, use_lock)


def run_simulation(use_lock: bool) -> int:
    """Proses semua pesanan dan kembalikan nilai counter akhir."""
    global processed_count

    processed_count = 0
    order_ids = list(range(1, NUM_ORDERS + 1))
    order_groups = [order_ids[index::NUM_WORKERS] for index in range(NUM_WORKERS)]
    threads = [
        threading.Thread(target=worker, args=(group, use_lock))
        for group in order_groups
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return processed_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulasi pesanan FoodGo")
    parser.add_argument(
        "--mode",
        choices=("both", "no-lock", "with-lock"),
        default="both",
        help="Kondisi sinkronisasi yang dijalankan (default: both)",
    )
    args = parser.parse_args()

    if args.mode == "both":
        modes = (("tanpa Lock", False), ("dengan Lock", True))
    elif args.mode == "no-lock":
        modes = (("tanpa Lock", False),)
    else:
        modes = (("dengan Lock", True),)

    for label, use_lock in modes:
        result = run_simulation(use_lock)
        print(
            f"[{label}] Total pesanan diproses: {result} "
            f"(seharusnya {NUM_ORDERS})"
        )
        if result != NUM_ORDERS:
            print("RACE CONDITION TERDETEKSI: counter tidak sesuai.")


if __name__ == "__main__":
    main()
