import os
import re
import sys
from pathlib import Path
from PIL import Image
import pytesseract

# Tesseractのパスを指定（Windows用）
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ベースフォルダパス
base_folder = Path.home() / "Desktop/リネーム実験場/セブン銀行"

if not base_folder.exists():
    print(f"フォルダが見つかりません: {base_folder}")
    sys.exit(1)

print(f"処理開始: {base_folder}\n")

count = 0

# サブフォルダを走査
for subfolder in base_folder.rglob('*'):
    if subfolder.is_dir():
        # JPG/PNG ファイルをスキャン
        for filename in sorted(os.listdir(subfolder)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = subfolder / filename

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
                        new_filepath = subfolder / new_filename

                        # リネーム
                        filepath.rename(new_filepath)
                        print(f"✓ {new_filename}")
                        count += 1
                    else:
                        print(f"✗ {filename} (日付が見つかりません)")

                except Exception as e:
                    print(f"✗ {filename} (エラー: {e})")

print(f"\n完了！{count}個のファイルをリネームしました。")
