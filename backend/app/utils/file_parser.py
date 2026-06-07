"""文件解析工具 — 从上传的文件中提取纯文本内容。

支持格式: .txt, .md, .json, .xml, .csv, .html, .doc, .docx, .pdf
"""
from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from PyPDF2 import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".xml", ".csv", ".html", ".htm", ".doc", ".docx", ".pdf"}


def extract_text(filename: str, content: bytes) -> str:
    """从文件二进制内容中提取纯文本。

    Parameters
    ----------
    filename: 原始文件名，用于判断格式。
    content: 文件二进制内容。

    Returns
    -------
    str: 提取的纯文本，保留段落换行。

    Raises
    ------
    ValueError: 不支持的文件格式或解析失败。
    """
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}，支持: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    # 纯文本系列
    if ext in {".txt", ".md", ".json", ".xml", ".csv", ".html", ".htm"}:
        return _decode_text(content)

    # Word 文档
    if ext in {".doc", ".docx"}:
        return _parse_docx(content)

    # PDF
    if ext == ".pdf":
        return _parse_pdf(content)

    raise ValueError(f"不支持的文件格式: {ext}")


def _decode_text(content: bytes) -> str:
    """尝试多种编码解码纯文本。"""
    for encoding in ("utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"):
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return content.decode("utf-8", errors="replace")


def _parse_docx(content: bytes) -> str:
    """解析 .docx 文件，提取段落文本。"""
    import io

    doc = DocxDocument(io.BytesIO(content))
    paragraphs: list[str] = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _parse_pdf(content: bytes) -> str:
    """解析 PDF 文件，提取每页文本。"""
    import io

    reader = PdfReader(io.BytesIO(content))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            pages.append(text.strip())
    return "\n\n".join(pages)
