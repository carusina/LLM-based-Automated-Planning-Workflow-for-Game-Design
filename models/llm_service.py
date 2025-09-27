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

# Gemini
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    available_providers["gemini"] = True
    logger.info("Google Generative AI library loaded successfully")
except ImportError:
    available_providers["gemini"] = False
    logger.warning("Google Generative AI library not found. Gemini provider will not be available.")

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
        SUPPORTED_MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        DEFAULT_MODEL = "gpt-4o"
        
        def __init__(self, model_name: str = None):
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not set in environment.")
            self.client = openai.OpenAI(api_key=api_key)
            self.model_name = model_name or self.DEFAULT_MODEL
            logger.info(f"OpenAIService initialized with model: {self.model_name}")

        def generate(self, prompt: str, **kwargs) -> str:
            try:
                params = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.pop('temperature', 0.7),
                    "max_tokens": kwargs.pop('max_tokens', 4096),
                }
                params.update(kwargs)
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content.strip()
            except Exception as e:
                error_info = ErrorUtils.handle_error(logger, e, "Error generating text with OpenAI")
                raise type(e)(f"OpenAI API error: {error_info['error']}")
                
        def get_supported_models(self) -> List[str]:
            return self.SUPPORTED_MODELS
        
        def get_default_model(self) -> str:
            return self.DEFAULT_MODEL
else:
    class OpenAIService:
        def __init__(self, *args, **kwargs):
            raise ImportError("OpenAI library not installed.")


# Anthropic 구현은 라이브러리가 있을 때만 정의
if available_providers["anthropic"]:
    class AnthropicService(BaseLLM):
        """Anthropic Claude API를 사용하는 LLM 서비스 구현"""
        SUPPORTED_MODELS = ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        DEFAULT_MODEL = "claude-3-5-sonnet-20240620"
        
        def __init__(self, model_name: str = None):
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY is not set in environment.")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_name = model_name or self.DEFAULT_MODEL
            logger.info(f"AnthropicService initialized with model: {self.model_name}")

        def generate(self, prompt: str, **kwargs) -> str:
            try:
                params = {
                    "model": self.model_name,
                    "max_tokens": kwargs.pop('max_tokens', 4096),
                    "temperature": kwargs.pop('temperature', 0.7),
                    "messages": [{"role": "user", "content": prompt}]
                }
                params.update(kwargs)
                response = self.client.messages.create(**params)
                return response.content[0].text
            except Exception as e:
                error_info = ErrorUtils.handle_error(logger, e, "Error generating text with Anthropic")
                raise type(e)(f"Anthropic API error: {error_info['error']}")
        
        def get_supported_models(self) -> List[str]:
            return self.SUPPORTED_MODELS
        
        def get_default_model(self) -> str:
            return self.DEFAULT_MODEL
else:
    class AnthropicService:
        def __init__(self, *args, **kwargs):
            raise ImportError("Anthropic library not installed.")

# Gemini 구현은 라이브러리가 있을 때만 정의
if available_providers["gemini"]:
    class GeminiService(BaseLLM):
        """Google Gemini API를 사용하는 LLM 서비스 구현"""
        SUPPORTED_MODELS = ["gemini-2.0-flash", "gemini-2.5-flash"]
        DEFAULT_MODEL = "gemini-2.0-flash"
        
        def __init__(self, model_name: str = None):
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not set in environment.")
            genai.configure(api_key=api_key)
            self.model_name = model_name or self.DEFAULT_MODEL
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"GeminiService initialized with model: {self.model_name}")

        def generate(self, prompt: str, **kwargs) -> str:
            """
            Gemini API를 사용하여 텍스트 생성. 안전 설정을 조정하여 차단 가능성을 줄임.
            """
            try:
                generation_config = {
                    "temperature": kwargs.pop('temperature', 0.7),
                    "max_output_tokens": kwargs.pop('max_tokens', 4096),
                }
                
                # 안전 설정: 유해 콘텐츠 차단 임계값을 낮춤 (덜 민감하게 반응)
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                }

                response = self.client.generate_content(
                    prompt, 
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                # .text 접근자 사용 전, 응답 유효성 검사
                if response.parts:
                    return response.text.strip()
                
                # 응답이 비어있는 경우, 차단 원인 분석
                finish_reason = response.candidates[0].finish_reason if response.candidates else 0
                if finish_reason == 2: # SAFETY
                    block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Unknown"
                    raise ValueError(f"Gemini response was blocked for safety reasons. Reason: {block_reason}. Try rephrasing your prompt.")
                else:
                    raise ValueError(f"Gemini returned an empty response. Finish Reason: {finish_reason}")

            except (ValueError, TypeError) as ve:
                # 이미 내용이 명확한 ValueError는 그대로 전달
                raise ve
            except Exception as e:
                error_info = ErrorUtils.handle_error(logger, e, "Error generating text with Gemini")
                raise type(e)(f"Gemini API error: {error_info['error']}")
                
        def get_supported_models(self) -> List[str]:
            return self.SUPPORTED_MODELS
        
        def get_default_model(self) -> str:
            return self.DEFAULT_MODEL
else:
    class GeminiService:
        def __init__(self, *args, **kwargs):
            raise ImportError("Google Generative AI library not installed.")


class LLMServiceFactory:
    """LLM 서비스 객체를 생성하는 팩토리 클래스"""
    PROVIDERS = {}
    if available_providers.get("openai", False): PROVIDERS["openai"] = OpenAIService
    if available_providers.get("anthropic", False): PROVIDERS["anthropic"] = AnthropicService
    if available_providers.get("gemini", False): PROVIDERS["gemini"] = GeminiService
    # ... (Mistral, Cohere 등 다른 제공자 로딩은 생략)
        
    @staticmethod
    def get_available_providers() -> List[str]:
        return list(LLMServiceFactory.PROVIDERS.keys())
    
    @staticmethod
    def get_provider_models(provider: str) -> Dict[str, List[str]]:
        if provider not in LLMServiceFactory.PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        provider_class = LLMServiceFactory.PROVIDERS[provider]
        return {"models": provider_class.SUPPORTED_MODELS, "default": provider_class.DEFAULT_MODEL}
    
    @staticmethod
    def create(provider: str = None, model_name: str = None) -> BaseLLM:
        load_dotenv()
        if provider is None:
            provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini") # 기본값을 gemini로 설정
        
        provider = provider.lower()
        if provider in LLMServiceFactory.PROVIDERS:
            return LLMServiceFactory.PROVIDERS[provider](model_name=model_name)
        else:
            available = ", ".join(LLMServiceFactory.get_available_providers())
            error_msg = f"Unsupported LLM provider: {provider}. Available: {available}"
            logger.error(error_msg)
            raise ValueError(error_msg)


class LLMService:
    """LLM 서비스 통합 인터페이스"""
    def __init__(self, llm_client: BaseLLM = None, provider: str = None, model_name: str = None, retry_count: int = 3, retry_delay: float = 1.0):
        if llm_client:
            self.client = llm_client
        else:
            self.client = LLMServiceFactory.create(provider, model_name)
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        logger.info(f"LLMService initialized with client: {type(self.client).__name__}")

    def generate(self, prompt: str, **kwargs) -> str:
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
                    time.sleep(self.retry_delay * (2 ** (attempt - 1)))
        error_info = ErrorUtils.handle_error(logger, last_error, "Error in LLM generation after multiple retries")
        raise type(last_error)(f"LLM generation error: {error_info['error']}")
    
    # ... (get_supported_providers, get_provider_details 등 나머지 메서드는 생략) ...
