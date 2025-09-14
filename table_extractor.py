# table_extractor.py
from img2table.document import Image
from img2table.ocr import EasyOCR
import json

def process_table(filepath):
    """
    این تابع یک مسیر تصویر می‌گیرد، جداول موجود در تصویر را استخراج می‌کند
    و خروجی JSON آماده ذخیره یا نمایش می‌دهد.
    """

    # ==== 1. بارگذاری OCR با PaddleOCR ====
    ocr = EasyOCR(lang=["en"])  # زبان انگلیسی، بدون GPU

    # ==== 2. بارگذاری تصویر جدول ====
    doc = Image(filepath, detect_rotation=True)  # مسیر تصویر جدول

    # ==== 3. استخراج جداول ====
    tables = doc.extract_tables(
        ocr=ocr,
        implicit_rows=False,
        implicit_columns=False,
        borderless_tables=False,  # جداول با خطوط واضح دقیق‌تر
        min_confidence=70         # فقط سلول‌های با اطمینان بالا
    )

    # ==== 4. آماده‌سازی خروجی JSON ====
    all_tables = []
    for t_id, table in enumerate(tables):
        print(f"\n📌 جدول {t_id+1}:")
        print(table.df)  # نمایش جدول به صورت DataFrame در کنسول

        table_json = []
        for id_row, row in enumerate(table.content.values()):
            row_data = []
            for id_col, cell in enumerate(row):
                row_data.append({
                    "row": id_row,
                    "col": id_col,
                    "bbox": [cell.bbox.x1, cell.bbox.y1, cell.bbox.x2, cell.bbox.y2],
                    "text": cell.value
                })
            table_json.append(row_data)
        all_tables.append(table_json)

    # اگر بخواهیم خروجی JSON ذخیره شود:
    output_file = "tables_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_tables, f, ensure_ascii=False, indent=4)

    print(f"\n✅ استخراج جدول تمام شد. خروجی در {output_file} ذخیره شد.")

    # برگرداندن خروجی برای استفاده در Flask یا دیگر برنامه‌ها
    return all_tables
