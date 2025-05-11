"""
LLMService: 추상화된 LLM 호출 인터페이스 (OpenAI, Anthropic 등 지원)

다양한 LLM 제공자(OpenAI, Anthropic 등)를 추상화하여 일관된 인터페이스 제공
각 LLM 제공자별 구현 클래스와 팩토리 패턴 사용
"""
import os
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
from dotenv import load_dotenv

# 상대 경로 모듈 임포트
from .utils import LoggingUtils, ErrorUtils

# 로깅 설정
logger = LoggingUtils.setup_logger(__name__)

# 선택적 임포트 - 없으면 무시
available_providers = {}

# OpenAI
try:
    import openai
    available_providers["openai"] = True
    logger.info("OpenAI library loaded successfully")
except ImportError:
    available_providers["openai"] = False
    logger.warning("OpenAI library not found. OpenAI provider will not be available.")

# Anthropic
try:
    import anthropic
    available_providers["anthropic"] = True
    logger.info("Anthropic library loaded successfully")
except ImportError:
    available_providers["anthropic"] = False
    logger.warning("Anthropic library not found. Claude provider will not be available.")

# Mistral (선택적으로 임포트)
try:
    import mistralai.client
    available_providers["mistral"] = True
    logger.info("Mistral AI library loaded successfully")
except ImportError:
    available_providers["mistral"] = False
    logger.debug("Mistral AI library not found. Mistral provider will not be available.")

# Cohere (선택적으로 임포트)
try:
    import cohere
    available_providers["cohere"] = True
    logger.info("Cohere library loaded successfully")
except ImportError:
    available_providers["cohere"] = False
    logger.debug("Cohere library not found. Cohere provider will not be available.")


class BaseLLM(ABC):
    """LLM 서비스의 기본 추상 클래스"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """LLM에 프롬프트를 전달하고 응답을 반환하는 추상 메서드"""
        pass
        
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """지원하는 모델 목록 반환"""
        pass
        
    @abstractmethod
    def get_default_model(self) -> str:
        """기본 모델명 반환"""
        pass


# OpenAI 구현은 라이브러리가 있을 때만 정의
if available_providers["openai"]:
    class OpenAIService(BaseLLM):
        """OpenAI API를 사용하는 LLM 서비스 구현"""
        
        # 지원 모델 목록
        SUPPORTED_MODELS = [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        DEFAULT_MODEL = "gpt-4o"
        
        def __init__(self, model_name: str = None):
            """
            OpenAI API 연결 설정
            
            Args:
                model_name (str, optional): 사용할 OpenAI 모델명. 기본값: DEFAULT_MODEL
            """
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY is not set in environment")
                raise ValueError("OPENAI_API_KEY is not set in environment.")
            
            self.client = openai.OpenAI(api_key=api_key)
            self.model_name = model_name or self.DEFAULT_MODEL
            logger.info(f"OpenAIService initialized with model: {self.model_name}")

        def generate(self, prompt: str, **kwargs) -> str:
            """
            OpenAI API를 사용하여 텍스트 생성
            
            Args:
                prompt (str): LLM에 전달할 프롬프트
                **kwargs: 추가 설정 (temperature, max_tokens 등)
                
            Returns:
                str: 생성된 텍스트
                
            Raises:
                Exception: API 호출 실패 시
            """
            try:
                # 실제 사용할 매개변수 준비
                params = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.pop('temperature', 0.7),
                    "max_tokens": kwargs.pop('max_tokens', 4096),
                }
                
                # 추가 매개변수 병합
                params.update(kwargs)
                
                # API 호출
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content.strip()
            except Exception as e:
                error_info = ErrorUtils.handle_error(
                    logger, e, "Error generating text with OpenAI")
                raise type(e)(f"OpenAI API error: {error_info['error']}")
                
        def get_supported_models(self) -> List[str]:
            """지원하는 모델 목록 반환"""
            return self.SUPPORTED_MODELS
        
        def get_default_model(self) -> str:
            """기본 모델명 반환"""
            return self.DEFAULT_MODEL
else:
    # 더미 클래스
    class OpenAIService:
        def __init__(self, *args, **kwargs):
            raise ImportError("OpenAI library not installed. Run 'pip install openai' to use this provider.")


# Anthropic 구현은 라이브러리가 있을 때만 정의
if available_providers["anthropic"]:
    class AnthropicService(BaseLLM):
        """Anthropic Claude API를 사용하는 LLM 서비스 구현"""
        
        # 지원 모델 목록
        SUPPORTED_MODELS = [
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]
        DEFAULT_MODEL = "claude-3-5-sonnet-20240620"
        
        def __init__(self, model_name: str = None):
            """
            Anthropic API 연결 설정
            
            Args:
                model_name (str, optional): 사용할 Anthropic 모델명. 기본값: DEFAULT_MODEL
            """
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.error("ANTHROPIC_API_KEY is not set in environment")
                raise ValueError("ANTHROPIC_API_KEY is not set in environment.")
            
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_name = model_name or self.DEFAULT_MODEL
            logger.info(f"AnthropicService initialized with model: {self.model_name}")

        def generate(self, prompt: str, **kwargs) -> str:
            """
            Anthropic API를 사용하여 텍스트 생성
            
            Args:
                prompt (str): LLM에 전달할 프롬프트
                **kwargs: 추가 설정 (temperature, max_tokens 등)
                
            Returns:
                str: 생성된 텍스트
                
            Raises:
                Exception: API 호출 실패 시
            """
            try:
                # 실제 사용할 매개변수 준비
                params = {
                    "model": self.model_name,
                    "max_tokens": kwargs.pop('max_tokens', 4096),
                    "temperature": kwargs.pop('temperature', 0.7),
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                
                # 추가 매개변수 병합
                params.update(kwargs)
                
                # API 호출
                response = self.client.messages.create(**params)
                return response.content[0].text
            except Exception as e:
                error_info = ErrorUtils.handle_error(
                    logger, e, "Error generating text with Anthropic")
                raise type(e)(f"Anthropic API error: {error_info['error']}")
        
        def get_supported_models(self) -> List[str]:
            """지원하는 모델 목록 반환"""
            return self.SUPPORTED_MODELS
        
        def get_default_model(self) -> str:
            """기본 모델명 반환"""
            return self.DEFAULT_MODEL
else:
    # 더미 클래스
    class AnthropicService:
        def __init__(self, *args, **kwargs):
            raise ImportError("Anthropic library not installed. Run 'pip install anthropic' to use this provider.")


class LLMServiceFactory:
    """LLM 서비스 객체를 생성하는 팩토리 클래스"""
    
    # 지원하는 LLM 제공자 매핑
    PROVIDERS = {}
    
    # 사용 가능한 제공자 초기화
    if available_providers.get("openai", False):
        PROVIDERS["openai"] = OpenAIService
    if available_providers.get("anthropic", False):
        PROVIDERS["anthropic"] = AnthropicService
    if available_providers.get("mistral", False):
        from .mistral_service import MistralService
        PROVIDERS["mistral"] = MistralService
    if available_providers.get("cohere", False):
        from .cohere_service import CohereService
        PROVIDERS["cohere"] = CohereService
        
    @staticmethod
    def get_available_providers() -> List[str]:
        """사용 가능한 LLM 제공자 목록 반환"""
        return list(LLMServiceFactory.PROVIDERS.keys())
    
    @staticmethod
    def get_provider_models(provider: str) -> Dict[str, List[str]]:
        """지정된 제공자의 모델 정보 반환"""
        if provider not in LLMServiceFactory.PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")
            
        provider_class = LLMServiceFactory.PROVIDERS[provider]
        return {
            "models": provider_class.SUPPORTED_MODELS,
            "default": provider_class.DEFAULT_MODEL
        }
    
    @staticmethod
    def create(provider: str = None, model_name: str = None) -> BaseLLM:
        """
        요청된 LLM 제공자와 모델에 맞는 서비스 객체 생성
        
        Args:
            provider (str, optional): LLM 제공자 ('openai' 또는 'anthropic'). 
                기본값: .env 파일의 DEFAULT_LLM_PROVIDER 또는 'openai'
            model_name (str, optional): 사용할 모델명. 
                기본값: 각 제공자의 기본 모델
            
        Returns:
            BaseLLM: LLM 서비스 인스턴스
            
        Raises:
            ValueError: 지원하지 않는 LLM 제공자 지정 시
        """
        load_dotenv()
        provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
        
        if provider in LLMServiceFactory.PROVIDERS:
            provider_class = LLMServiceFactory.PROVIDERS[provider]
            return provider_class(model_name=model_name)
        else:
            available = ", ".join(LLMServiceFactory.get_available_providers())
            if not available:
                error_msg = "No LLM providers available. Please install at least one of: 'openai', 'anthropic'"
            else:
                error_msg = f"Unsupported LLM provider: {provider}. Available providers: {available}"
            logger.error(error_msg)
            raise ValueError(error_msg)


class LLMService:
    """
    LLM 서비스 통합 인터페이스
    
    여러 LLM 제공자를 추상화하여 일관된 인터페이스 제공
    BaseLLM 인스턴스를 주입하거나 provider와 model_name을 지정하여 사용
    """
    def __init__(self, 
                 llm_client: BaseLLM = None, 
                 provider: str = None,
                 model_name: str = None,
                 retry_count: int = 3,
                 retry_delay: float = 1.0):
        """
        LLM 서비스 초기화
        
        Args:
            llm_client (BaseLLM, optional): 직접 주입할 LLM 클라이언트
            provider (str, optional): LLM 제공자 ('openai', 'anthropic' 등)
            model_name (str, optional): 사용할 모델명
            retry_count (int, optional): 실패 시 재시도 횟수 (기본값: 3)
            retry_delay (float, optional): 재시도 간 대기 시간(초) (기본값: 1.0)
        """
        if llm_client:
            self.client = llm_client
        else:
            self.client = LLMServiceFactory.create(provider, model_name)
        
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        logger.info(f"LLMService initialized with client: {type(self.client).__name__}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        LLM에 프롬프트를 전달하고 응답을 반환
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            **kwargs: 추가 설정 (temperature, max_tokens 등)
            
        Returns:
            str: 생성된 텍스트
            
        Raises:
            Exception: LLM 호출 실패 시
        """
        attempt = 0
        last_error = None
        
        while attempt < self.retry_count:
            try:
                return self.client.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                attempt += 1
                logger.warning(f"Attempt {attempt}/{self.retry_count} failed: {e}")
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay * (2 ** (attempt - 1)))  # 지수 백오프 적용
                    
        # 모든 재시도 실패 시 마지막 에러 반환
        error_info = ErrorUtils.handle_error(
            logger, last_error, "Error in LLM generation after multiple retries")
        raise type(last_error)(f"LLM generation error: {error_info['error']}")
    
    def get_supported_providers(self) -> List[str]:
        """
        지원되는 LLM 제공자 목록 반환
        
        Returns:
            List[str]: 지원 제공자 목록
        """
        return LLMServiceFactory.get_available_providers()
    
    def get_provider_details(self, provider: str = None) -> Dict[str, Any]:
        """
        지정된 제공자의 모델 정보 반환
        
        Args:
            provider (str, optional): 정보를 조회할 제공자
                None인 경우 현재 사용 중인 제공자 사용
                
        Returns:
            Dict[str, Any]: 모델 정보
        """
        if provider is None:
            if not self.client:
                raise ValueError("No LLM client initialized")
            provider = type(self.client).__name__
            # Remove 'Service' 접미사
            if provider.endswith('Service'):
                provider = provider[:-7].lower()
        
        return LLMServiceFactory.get_provider_models(provider)
    
    def estimate_tokens(self, text: str) -> int:
        """
        텍스트의 대략적인 토큰 수 추정
        
        Args:
            text (str): 토큰 수를 추정할 텍스트
            
        Returns:
            int: 추정 토큰 수
        """
        # 간단한 추정: 영어 기준 약 4글자당 1토큰, 한글 기준 약 2글자당 1토큰
        # 실제 토큰화는 모델에 따라 다를 수 있음
        english_chars = sum(1 for c in text if ord(c) < 128)
        korean_chars = len(text) - english_chars
        
        # 토큰 수 추정 (대략적인 계산)
        estimated_tokens = int(english_chars / 4 + korean_chars / 2)
        
        # 최소 토큰 수 보장
        return max(1, estimated_tokens)
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """
        여러 프롬프트를 일괄 처리하여 응답 생성
        
        Args:
            prompts (List[str]): 처리할 프롬프트 목록
            **kwargs: 추가 설정 (temperature, max_tokens 등)
            
        Returns:
            List[str]: 각 프롬프트에 대한 응답 목록
            
        Raises:
            Exception: 생성 중 오류 발생 시
        """
        responses = []
        errors = []
        
        # 각 프롬프트에 대해 병렬 처리 대신 순차적으로 처리
        for i, prompt in enumerate(prompts):
            try:
                response = self.generate(prompt, **kwargs)
                responses.append(response)
                logger.info(f"Successfully generated response for prompt {i+1}/{len(prompts)}")
            except Exception as e:
                error_info = ErrorUtils.handle_error(
                    logger, e, f"Error generating response for prompt {i+1}/{len(prompts)}")
                errors.append({
                    "prompt_index": i,
                    "error": str(e),
                    "details": error_info
                })
                responses.append(None)  # 오류 발생 시 None 추가
        
        # 오류 정보 로깅
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during batch generation")
            for error in errors:
                logger.warning(f"Error for prompt {error['prompt_index']}: {error['error']}")
        
        return responses