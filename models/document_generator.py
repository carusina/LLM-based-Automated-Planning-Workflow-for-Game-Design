"""
document_generator.py

문서 저장 모듈
- Markdown, Plain Text, PDF 형식 지원
- output/ 디렉토리에 파일 저장
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil
import subprocess
import tempfile

class DocumentGenerator:
    """
    문서 저장 모듈
    
    LLM이 생성한 콘텐츠를 다양한 형식(.md, .txt, .pdf)으로 저장합니다.
    """
    
    def __init__(self, output_dir: str = None):
        """
        문서 생성기 초기화
        
        Args:
            output_dir (str, optional): 출력 디렉토리 경로
        """
        # 출력 디렉토리 설정 (상대 경로 사용)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = output_dir or os.path.join(base_dir, 'output')
        
        # 출력 디렉토리 생성 (없는 경우)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Output directory set to: {self.output_dir}")

    def save_markdown(self, filename: str, content: str) -> str:
        """
        Markdown(.md) 형식으로 저장
        
        Args:
            filename (str): 파일명(확장자 제외)
            content (str): 저장할 내용
            
        Returns:
            str: 저장된 파일의 절대 경로
        """
        # 확장자가 이미 포함된 경우 처리
        if not filename.endswith('.md'):
            filename = f"{filename}.md"
        
        # 절대 경로 구성
        path = os.path.join(self.output_dir, filename)
        
        # 파일 저장
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Markdown file saved at: {path}")
        return path

    def save_text(self, filename: str, content: str) -> str:
        """
        Plain Text(.txt) 형식으로 저장
        
        Args:
            filename (str): 파일명(확장자 제외)
            content (str): 저장할 내용
            
        Returns:
            str: 저장된 파일의 절대 경로
        """
        # 확장자가 이미 포함된 경우 처리
        if not filename.endswith('.txt'):
            filename = f"{filename}.txt"
        
        # 절대 경로 구성
        path = os.path.join(self.output_dir, filename)
        
        # 파일 저장
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Text file saved at: {path}")
        return path

    def save_pdf(self, filename: str, markdown_content: str) -> str:
        """
        PDF(.pdf) 형식으로 저장
        
        Markdown 내용을 PDF로 변환하여 저장합니다.
        Pandoc을 사용하여 변환을 수행합니다.
        
        Args:
            filename (str): 파일명(확장자 제외)
            markdown_content (str): 저장할 Markdown 내용
            
        Returns:
            str: 저장된 파일의 절대 경로
            
        Raises:
            RuntimeError: PDF 변환 실패 시
        """
        # 확장자가 이미 포함된 경우 처리
        if not filename.endswith('.pdf'):
            filename = f"{filename}.pdf"
        
        # 절대 경로 구성
        path = os.path.join(self.output_dir, filename)
        
        # 임시 Markdown 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', encoding='utf-8', delete=False) as temp_md:
            temp_md.write(markdown_content)
            temp_md_path = temp_md.name
        
        try:
            # Pandoc을 사용하여 PDF 변환
            self.logger.info(f"Converting Markdown to PDF using Pandoc...")
            result = subprocess.run(
                [
                    'pandoc',
                    temp_md_path,
                    '-o', path,
                    '--pdf-engine=xelatex',
                    '-V', 'geometry:margin=1in',
                    '-V', 'fontsize=11pt'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"PDF file saved at: {path}")
            return path
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Pandoc PDF conversion failed: {e.stderr}")
            raise RuntimeError(f"PDF conversion failed: {e.stderr}")
            
        except FileNotFoundError:
            self.logger.error("Pandoc not found. Please install Pandoc.")
            raise RuntimeError("Pandoc not found. Please install Pandoc to generate PDF files.")
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_md_path):
                os.remove(temp_md_path)
    
    def save_document(self, filename: str, content: str, format_type: str = "md") -> str:
        """
        지정된 형식으로 문서 저장
        
        Args:
            filename (str): 파일명(확장자 제외)
            content (str): 저장할 내용
            format_type (str, optional): 저장 형식 ("md", "txt", "pdf")
            
        Returns:
            str: 저장된 파일의 절대 경로
            
        Raises:
            ValueError: 지원하지 않는 형식 지정 시
        """
        format_type = format_type.lower()
        
        if format_type == "md":
            return self.save_markdown(filename, content)
        elif format_type == "txt":
            return self.save_text(filename, content)
        elif format_type == "pdf":
            return self.save_pdf(filename, content)
        else:
            error_msg = f"Unsupported format type: {format_type}. Supported formats: md, txt, pdf"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def save_multiple_formats(self, filename: str, content: str, formats: List[str] = None) -> Dict[str, str]:
        """
        여러 형식으로 동시에 저장
        
        Args:
            filename (str): 파일명(확장자 제외)
            content (str): 저장할 내용
            formats (List[str], optional): 저장할 형식 목록 (기본: ["md", "pdf"])
            
        Returns:
            Dict[str, str]: 형식별 저장된 파일 경로
                {
                    "md": "/path/to/file.md",
                    "pdf": "/path/to/file.pdf",
                    ...
                }
        """
        formats = formats or ["md", "pdf"]
        result = {}
        
        for fmt in formats:
            try:
                path = self.save_document(filename, content, fmt)
                result[fmt] = path
            except Exception as e:
                self.logger.error(f"Failed to save in {fmt} format: {e}")
                result[fmt] = None
        
        return result
    
    def copy_assets(self, source_dir: str, target_subdir: str = None) -> List[str]:
        """
        문서 관련 자산 파일(이미지 등) 복사
        
        Args:
            source_dir (str): 소스 자산 디렉토리 경로
            target_subdir (str, optional): 대상 하위 디렉토리명 (output/ 내부)
            
        Returns:
            List[str]: 복사된 파일 경로 목록
        """
        # 대상 디렉토리 경로 구성
        if target_subdir:
            target_dir = os.path.join(self.output_dir, target_subdir)
            os.makedirs(target_dir, exist_ok=True)
        else:
            target_dir = self.output_dir
        
        # 소스 디렉토리 확인
        if not os.path.isdir(source_dir):
            self.logger.error(f"Source directory does not exist: {source_dir}")
            return []
        
        # 파일 복사
        copied_files = []
        for item in os.listdir(source_dir):
            src_path = os.path.join(source_dir, item)
            dst_path = os.path.join(target_dir, item)
            
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
                copied_files.append(dst_path)
                self.logger.info(f"Copied asset: {src_path} -> {dst_path}")
        
        return copied_files
