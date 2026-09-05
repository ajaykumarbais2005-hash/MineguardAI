from dataclasses import dataclass


@dataclass(frozen=True)
class OCRExtraction:
    text: str
    confidence: float
    detected_fields: dict[str, str]
    mode: str = "DEMO"


def extract_demo_text(file_name: str, content: bytes) -> OCRExtraction:
    text = content.decode("utf-8", errors="ignore")[:5000]
    if not text.strip():
        text = f"DEMO OCR extract for {file_name}."
    return OCRExtraction(text=text, confidence=0.82, detected_fields={"document_type": "DEMO_OCR"})
