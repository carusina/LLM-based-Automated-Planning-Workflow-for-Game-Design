"""
utils.py

공통 유틸리티 모듈
- 경로 관련 유틸리티
- 공통 로깅 설정
- 오류 처리 함수
"""

import os
import logging
import traceback
from typing import Dict, List, Any, Optional
from pathlib import Path

class PathUtils:
    """
    경로 관련 유틸리티 클래스
    
    일관된 방식으로 프로젝트 내 디렉토리와 파일 경로를 관리합니다.
    모든 경로는 상대 경로를 사용합니다.
    """
    
    @staticmethod
    def get_project_root() -> str:
        """
        프로젝트 루트 디렉토리 경로 반환
        
        Returns:
            str: 프로젝트 루트 디렉토리의 절대 경로
        """
        # 현재 파일(utils.py)의 디렉토리 확인
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 상위 디렉토리(프로젝트 루트) 경로 반환
        return os.path.dirname(current_dir)
    
    @staticmethod
    def get_models_dir() -> str:
        """
        models 디렉토리 경로 반환
        
        Returns:
            str: models 디렉토리의 절대 경로
        """
        return os.path.join(PathUtils.get_project_root(), 'models')
    
    @staticmethod
    def get_templates_dir() -> str:
        """
        templates 디렉토리 경로 반환
        
        Returns:
            str: templates 디렉토리의 절대 경로
        """
        return os.path.join(PathUtils.get_project_root(), 'templates')
    
    @staticmethod
    def get_output_dir() -> str:
        """
        output 디렉토리 경로 반환
        
        Returns:
            str: output 디렉토리의 절대 경로
        """
        output_dir = os.path.join(PathUtils.get_project_root(), 'output')
        # 디렉토리가 없으면 생성
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return output_dir
    
    @staticmethod
    def get_web_dir() -> str:
        """
        web 디렉토리 경로 반환
        
        Returns:
            str: web 디렉토리의 절대 경로
        """
        return os.path.join(PathUtils.get_project_root(), 'web')
    
    @staticmethod
    def get_assets_dir() -> str:
        """
        assets 디렉토리 경로 반환
        
        Returns:
            str: assets 디렉토리의 절대 경로
        """
        return os.path.join(PathUtils.get_project_root(), 'assets')
    
    @staticmethod
    def ensure_dir(dir_path: str) -> str:
        """
        지정된 디렉토리가 존재하는지 확인하고, 없으면 생성
        
        Args:
            dir_path (str): 확인할 디렉토리 경로
            
        Returns:
            str: 생성된 디렉토리 경로
        """
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @staticmethod
    def get_relative_path(path: str) -> str:
        """
        지정된 경로를 프로젝트 루트 기준 상대 경로로 변환
        
        Args:
            path (str): 변환할 경로
            
        Returns:
            str: 상대 경로
        """
        project_root = PathUtils.get_project_root()
        return os.path.relpath(path, project_root)

class LoggingUtils:
    """
    로깅 관련 유틸리티 클래스
    
    일관된 방식으로 로깅을 설정하고 관리합니다.
    """
    
    @staticmethod
    def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
        """
        로거 설정
        
        Args:
            name (str, optional): 로거 이름
            level (int, optional): 로깅 레벨
            
        Returns:
            logging.Logger: 설정된 로거 인스턴스
        """
        # 기본 로깅 설정
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 로거 생성
        return logging.getLogger(name or __name__)

class ErrorUtils:
    """
    오류 처리 관련 유틸리티 클래스
    
    일관된 방식으로 오류를 처리하고 관리합니다.
    """
    
    @staticmethod
    def handle_error(
        logger: logging.Logger,
        error: Exception,
        message: str = "오류가 발생했습니다",
        raise_error: bool = False
    ) -> Dict[str, Any]:
        """
        오류 처리
        
        Args:
            logger (logging.Logger): 로거 인스턴스
            error (Exception): 발생한 오류
            message (str, optional): 오류 메시지
            raise_error (bool, optional): 오류를 다시 발생시킬지 여부
            
        Returns:
            Dict[str, Any]: 오류 정보
                {
                    "error": 오류 메시지,
                    "type": 오류 유형,
                    "traceback": 스택 트레이스
                }
                
        Raises:
            Exception: raise_error가 True인 경우 오류를 다시 발생시킴
        """
        # 오류 정보 수집
        error_info = {
            "error": str(error),
            "type": type(error).__name__,
            "traceback": traceback.format_exc()
        }
        
        # 로깅
        logger.error(f"{message}: {error}")
        logger.debug(error_info["traceback"])
        
        # 필요시 오류 다시 발생
        if raise_error:
            raise error
        
        return error_info
