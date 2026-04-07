import csv
from datetime import datetime
from pathlib import Path
import speedtest

MIN_DOWNLOAD_MBPS = 50.0
MIN_UPLOAD_MBPS = 10.0
MAX_PING_MS = 50.0

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
ERRORS_DIR = BASE_DIR / "errors"
CSV_FILE = LOGS_DIR / "speed_log.csv"
ERROR_LOG_FILE = ERRORS_DIR / "error_log.txt"


def create_folders():
    LOGS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    ERRORS_DIR.mkdir(exist_ok=True)


def log_error(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with ERROR_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


def run_speed_test():
    tester = speedtest.Speedtest()

    tester.get_best_server()
    download_bps = tester.download()
    upload_bps = tester.upload()
    ping_ms = tester.results.ping
    server_name = tester.results.server.get("name", "Unknown")
    server_sponsor = tester.results.server.get("sponsor", "Unknown")

    download_mbps = download_bps / 1_000_000
    upload_mbps = upload_bps / 1_000_000

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "download_mbps": round(download_mbps, 2),
        "upload_mbps": round(upload_mbps, 2),
        "ping_ms": round(ping_ms, 2),
        "server_name": server_name,
        "server_sponsor": server_sponsor,
    }


def save_to_csv(result):
    csv_exists = CSV_FILE.exists()

    with CSV_FILE.open("a", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        if not csv_exists:
            writer.writerow([
                "timestamp",
                "download_mbps",
                "upload_mbps",
                "ping_ms",
                "server_name",
                "server_sponsor",
            ])

        writer.writerow([
            result["timestamp"],
            result["download_mbps"],
            result["upload_mbps"],
            result["ping_ms"],
            result["server_name"],
            result["server_sponsor"],
        ])


def create_slow_speed_report(result):
    is_slow = (
        result["download_mbps"] < MIN_DOWNLOAD_MBPS
        or result["upload_mbps"] < MIN_UPLOAD_MBPS
        or result["ping_ms"] > MAX_PING_MS
    )

    if not is_slow:
        return

    safe_timestamp = result["timestamp"].replace(":", "-").replace(" ", "_")
    report_file = REPORTS_DIR / f"slow_report_{safe_timestamp}.txt"

    with report_file.open("w", encoding="utf-8") as file:
        file.write("Internet Speed Alert Report\n")
        file.write("=" * 30 + "\n")
        file.write(f"Timestamp: {result['timestamp']}\n")
        file.write(f"Server: {result['server_name']} ({result['server_sponsor']})\n")
        file.write(f"Download: {result['download_mbps']} Mbps\n")
        file.write(f"Upload: {result['upload_mbps']} Mbps\n")
        file.write(f"Ping: {result['ping_ms']} ms\n")


def main():
    create_folders()

    try:
        result = run_speed_test()
        save_to_csv(result)
        create_slow_speed_report(result)
        print("Speed test complete. Log updated.")
    except Exception as error:
        log_error(str(error))
        print("Error occurred. Check errors folder.")


if __name__ == "__main__":
    main()
