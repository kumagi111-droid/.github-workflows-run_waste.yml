import pandas as pd

SOURCES = [
    {"type": "มูลฝอยทั่วไป", "sheet_id": "11UW2Y3ideUwO0s9JznnxoUZrNloxUxIbwKKNS7o8z3o", "gid": "1225643604"},
    {"type": "มูลฝอยติดเชื้อ", "sheet_id": "1GuxUTzMCkYmHiqDZDU9wCXafRehMbDZSgK9aYBtrOmk", "gid": "1124248259"},
    {"type": "มูลฝอยอันตราย", "sheet_id": "1G9FXgb1tJ5CxLB6mB6K76pALvncb7Yn2QO1MbCqLkRw", "gid": "752468467"},
    {"type": "มูลฝอยรีไซเคิล", "sheet_id": "1CJnGOlmPTRZn4hSjzFoLGHfhAsBhCYTaJwFyfc9Ohfg", "gid": "561302972"},
]

master_records = []

for src in SOURCES:
    url = f"https://docs.google.com/spreadsheets/d/{src['sheet_id']}/export?format=csv&gid={src['gid']}"
    print(f"กำลังดาวน์โหลดข้อมูล: {src['type']}...")
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการโหลด {src['type']}: {e}")
        continue

    date_col = "วันที่ลงข้อมูล"
    time_col = "เวลาที่ลงข้อมูล"
    recorder_col = "ชื่อผู้ลงข้อมูล"

    cols_to_exclude = ["ประทับเวลา", date_col, time_col, recorder_col]
    waste_cols = [c for c in df.columns if c not in cols_to_exclude and not str(c).startswith("Unnamed")]

    for _, row in df.iterrows():
        date_val = row.get(date_col)
        time_val = row.get(time_col, "")
        recorder_val = row.get(recorder_col, "ไม่ระบุ")

        if pd.isna(date_val) or str(date_val).strip() == "":
            continue

        for col in waste_cols:
            weight_val = row.get(col)
            try:
                weight = float(weight_val)
            except (ValueError, TypeError):
                weight = 0.0

            if weight > 0:
                dept_or_material = str(col).strip()
                category = src["type"]
                if "โภชนาการ" in dept_or_material and category == "มูลฝอยทั่วไป":
                    category = "มูลฝอยอินทรีย์"

                master_records.append({
                    "วันที่": date_val,
                    "เวลา": time_val,
                    "ประเภทมูลฝอย": category,
                    "จุดกำเนิด_หมวดหมู่": dept_or_material,
                    "น้ำหนัก_กก": round(weight, 2),
                    "ผู้บันทึก": recorder_val
                })

master_df = pd.DataFrame(master_records)
master_df["วันที่"] = pd.to_datetime(master_df["วันที่"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m-%d")
master_df = master_df.dropna(subset=["วันที่"])
master_df = master_df.sort_values(by=["วันที่", "เวลา"], ascending=[True, True])

master_df.to_csv("SHWMS_Master_Database.csv", index=False, encoding="utf-8-sig")
print(f"รวบรวมข้อมูลสำเร็จ: {len(master_df):,} รายการ")
