"""
QSIM Anomaly Detector
Reads live telemetry from the gateway and flags anomalous assets
using statistical and rule-based detection methods.
"""

import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
import time
import os

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://qsim.local")
CHECK_INTERVAL = 10  # seconds between checks

# ── Thresholds ────────────────────────────────────────────────────────────────
RULES = {
    "critical_health":      lambda r: r["health_score"] < 0.4,
    "warning_health":       lambda r: 0.4 <= r["health_score"] < 0.6,
    "high_temperature":     lambda r: r["temperature"] > 85.0,
    "extreme_vibration":    lambda r: r["vibration"] > 70.0,
    "fault_state":          lambda r: r["operational_state"] == "FAULT",
    "maintenance_state":    lambda r: r["operational_state"] == "MAINTENANCE",
}

SEVERITY = {
    "critical_health":   "CRITICAL",
    "warning_health":    "WARNING",
    "high_temperature":  "WARNING",
    "extreme_vibration": "CRITICAL",
    "fault_state":       "CRITICAL",
    "maintenance_state": "INFO",
}

def fetch_telemetry(limit=200):
    try:
        r = requests.get(f"{GATEWAY_URL}/telemetry?limit={limit}", timeout=5)
        return r.json().get("records", [])
    except Exception as e:
        print(f"[ERROR] Cannot reach gateway: {e}")
        return []

def fetch_assets():
    try:
        r = requests.get(f"{GATEWAY_URL}/assets", timeout=5)
        return r.json().get("assets", {})
    except:
        return {}

def detect_rule_anomalies(records):
    """Apply rule-based anomaly detection to latest record per asset."""
    latest = {}
    for r in records:
        aid = r["asset_id"]
        if aid not in latest:
            latest[aid] = r

    anomalies = []
    for asset_id, record in latest.items():
        for rule_name, rule_fn in RULES.items():
            if rule_fn(record):
                anomalies.append({
                    "asset_id":     asset_id,
                    "asset_type":   record.get("asset_type", "UNKNOWN"),
                    "rule":         rule_name,
                    "severity":     SEVERITY[rule_name],
                    "value": {
                        "temperature":   record["temperature"],
                        "vibration":     record["vibration"],
                        "health_score":  record["health_score"],
                        "state":         record["operational_state"]
                    },
                    "detected_at": datetime.utcnow().isoformat() + "Z"
                })
    return anomalies

def detect_statistical_anomalies(records):
    """
    Z-score based anomaly detection.
    Flags assets whose temperature or vibration is >2 std deviations from mean.
    """
    if len(records) < 10:
        return []

    df = pd.DataFrame(records)
    anomalies = []

    for metric in ["temperature", "vibration", "health_score"]:
        mean = df[metric].mean()
        std  = df[metric].std()
        if std == 0:
            continue

        for _, row in df.iterrows():
            z_score = abs((row[metric] - mean) / std)
            if z_score > 2.5:
                anomalies.append({
                    "asset_id":    row["asset_id"],
                    "asset_type":  row.get("asset_type", "UNKNOWN"),
                    "rule":        f"statistical_zscore_{metric}",
                    "severity":    "WARNING",
                    "z_score":     round(z_score, 2),
                    "value":       round(row[metric], 3),
                    "mean":        round(mean, 3),
                    "std":         round(std, 3),
                    "detected_at": datetime.utcnow().isoformat() + "Z"
                })

    return anomalies

def detect_trend_anomalies(records):
    """
    Trend detection: flag assets whose health score is consistently declining.
    Uses linear regression slope on last 20 records per asset.
    """
    df = pd.DataFrame(records)
    df["ingested_at"] = pd.to_datetime(df["ingested_at"])
    df = df.sort_values("ingested_at")

    anomalies = []
    for asset_id in df["asset_id"].unique():
        asset_df = df[df["asset_id"] == asset_id].tail(20)
        if len(asset_df) < 5:
            continue

        x = np.arange(len(asset_df))
        y = asset_df["health_score"].values
        slope = np.polyfit(x, y, 1)[0]

        if slope < -0.01:
            anomalies.append({
                "asset_id":    asset_id,
                "asset_type":  asset_df.iloc[0].get("asset_type", "UNKNOWN"),
                "rule":        "declining_health_trend",
                "severity":    "WARNING" if slope > -0.02 else "CRITICAL",
                "slope":       round(slope, 4),
                "description": f"Health score declining at {abs(slope):.4f} per reading",
                "detected_at": datetime.utcnow().isoformat() + "Z"
            })

    return anomalies

def print_report(rule_anomalies, stat_anomalies, trend_anomalies, assets):
    print("\n" + "="*70)
    print(f"  QSIM ANOMALY DETECTION REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    print(f"\n📊 ASSET STATES:")
    for aid, info in assets.items():
        state = info.get("state", "UNKNOWN")
        icon = {"RUNNING":"🟢","IDLE":"🟡","FAULT":"🔴","MAINTENANCE":"🟣"}.get(state,"⚪")
        print(f"   {icon} {aid} — {state}")

    total = len(rule_anomalies) + len(stat_anomalies) + len(trend_anomalies)
    print(f"\n🚨 ANOMALIES DETECTED: {total}")

    if rule_anomalies:
        print(f"\n── RULE-BASED ANOMALIES ({len(rule_anomalies)}) ──")
        for a in rule_anomalies:
            icon = "🔴" if a["severity"] == "CRITICAL" else "🟡" if a["severity"] == "WARNING" else "🔵"
            print(f"   {icon} [{a['severity']}] {a['asset_id']} ({a['asset_type']})")
            print(f"      Rule: {a['rule']}")
            print(f"      Values: temp={a['value']['temperature']}°C | "
                  f"vibr={a['value']['vibration']} | "
                  f"health={a['value']['health_score']} | "
                  f"state={a['value']['state']}")

    if stat_anomalies:
        print(f"\n── STATISTICAL ANOMALIES — Z-Score > 2.5 ({len(stat_anomalies)}) ──")
        seen = set()
        for a in stat_anomalies:
            key = (a["asset_id"], a["rule"])
            if key in seen:
                continue
            seen.add(key)
            print(f"   🟡 [WARNING] {a['asset_id']} — {a['rule']}")
            print(f"      Value: {a['value']} | Mean: {a['mean']} | Z-Score: {a['z_score']}")

    if trend_anomalies:
        print(f"\n── TREND ANOMALIES — Declining Health ({len(trend_anomalies)}) ──")
        for a in trend_anomalies:
            icon = "🔴" if a["severity"] == "CRITICAL" else "🟡"
            print(f"   {icon} [{a['severity']}] {a['asset_id']} — {a['description']}")

    if total == 0:
        print("\n   ✅ All assets nominal. No anomalies detected.")

    print("\n" + "="*70)

def save_report(rule_anomalies, stat_anomalies, trend_anomalies):
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_anomalies": len(rule_anomalies) + len(stat_anomalies) + len(trend_anomalies),
        "rule_based": rule_anomalies,
        "statistical": stat_anomalies,
        "trend": trend_anomalies
    }
    with open("anomaly_report.json", "w") as f:
        json.dump(report, f, indent=2)

def run():
    print("🔍 QSIM Anomaly Detector starting...")
    print(f"   Gateway: {GATEWAY_URL}")
    print(f"   Check interval: {CHECK_INTERVAL}s")
    print(f"   Detection methods: Rule-based, Z-Score Statistical, Trend Analysis")

    while True:
        records = fetch_telemetry(limit=200)
        assets  = fetch_assets()

        if not records:
            print("[WARN] No telemetry available yet. Retrying...")
            time.sleep(CHECK_INTERVAL)
            continue

        rule_anomalies  = detect_rule_anomalies(records)
        stat_anomalies  = detect_statistical_anomalies(records)
        trend_anomalies = detect_trend_anomalies(records)

        print_report(rule_anomalies, stat_anomalies, trend_anomalies, assets)
        save_report(rule_anomalies, stat_anomalies, trend_anomalies)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
