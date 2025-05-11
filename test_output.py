# test_output.py
from models.document_generator import DocumentGenerator

if __name__ == "__main__":
    doc = DocumentGenerator()
    path = doc.save_markdown("sample_gdd", "# 제목\n본문")
    print("생성된 파일:", path)
