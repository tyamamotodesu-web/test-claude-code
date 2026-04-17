import os
import re
import sys
from pathlib import Path
from PIL import Image
import pytesseract

# Tesseractのパスを指定（Windows用）
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# フォルダパス
folder_path = Path.home() / "Dropbox/仙台/10 債務整理案件/30 破産/7 手代木　直輝（ABC紹介一般座）"

if not folder_path.exists():
    print(f"フォルダが見つかりません: {folder_path}")
    sys.exit(1)

print(f"処理開始: {folder_path}\n")

# JPG/PNG ファイルをスキャン
for filename in sorted(os.listdir(folder_path)):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        filepath = folder_path / filename

        try:
            # OCR実行
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image, lang='jpn')

            # 日付抽出（「YYYY年MM月DD日～YYYY年MM月DD日」形式）
            date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日[～〜](\d{4})年(\d{1,2})月(\d{1,2})日'
            match = re.search(date_pattern, text)

            if match:
                y1, m1, d1, y2, m2, d2 = match.groups()
                date_str = f"{y1}{m1:0>2}{d1:0>2}-{y2}{m2:0>2}{d2:0>2}"
                new_filename = f"セブン銀行_{date_str}.jpg"
                new_filepath = folder_path / new_filename

                # リネーム
                filepath.rename(new_filepath)
                print(f"✓ {filename}")
                print(f"  → {new_filename}\n")
            else:
                print(f"✗ {filename} (日付が見つかりません)\n")

        except Exception as e:
            print(f"✗ {filename} (エラー: {e})\n")

print("完了！")
