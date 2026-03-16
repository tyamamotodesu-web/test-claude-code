import fitz  # pip install pymupdf

def stamp_pdf(input_path: str, output_path: str, text: str = "甲1") -> None:
    doc = fitz.open(input_path)
    page = doc[0]

    # フォントサイズと余白
    font_size = 36
    margin = 20

    # テキスト幅を計測して右上に配置
    text_width = fitz.get_text_length(text, fontname="helvetica", fontsize=font_size)
    x = page.rect.width - text_width - margin
    y = margin + font_size

    page.insert_text(
        (x, y),
        text,
        fontname="helvetica",
        fontsize=font_size,
        color=(1, 0, 0),  # 赤
    )

    doc.save(output_path)
    doc.close()
    print(f"保存: {output_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("使い方: python stamp_pdf.py input.pdf output.pdf")
        sys.exit(1)
    stamp_pdf(sys.argv[1], sys.argv[2])
