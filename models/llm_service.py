# models/llm_service.py
import openai
import anthropic
import json
import os
from typing import Dict, List, Any, Optional, Union

class LLMService:
    """LLM(대규모 언어 모델) 서비스를 처리하는 클래스"""
    
    def __init__(self, openai_api_key: str = None, anthropic_api_key: str = None):
        """
        LLM 서비스 초기화
        
        Args:
            openai_api_key: OpenAI API 키
            anthropic_api_key: Anthropic API 키
        """
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.anthropic_client = None
        
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    def generate_with_openai(self, 
                           prompt: str, 
                           model: str = "gpt-4-turbo",
                           temperature: float = 0.7, 
                           max_tokens: int = 2000) -> str:
        """
        OpenAI의 GPT 모델을 사용하여 텍스트 생성
        
        Args:
            prompt: 텍스트 생성을 위한 프롬프트
            model: 사용할 OpenAI 모델
            temperature: 창의성 조절 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            
        Returns:
            생성된 텍스트
        """
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "당신은 게임 기획 전문가입니다. 창의적이고 구체적인 게임 기획을 작성해 주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API 오류: {str(e)}")
            raise
    
    def generate_with_anthropic(self, 
                              prompt: str, 
                              model: str = "claude-3-opus-20240229", 
                              temperature: float = 0.7,
                              max_tokens: int = 2000) -> str:
        """
        Anthropic의 Claude 모델을 사용하여 텍스트 생성
        
        Args:
            prompt: 텍스트 생성을 위한 프롬프트
            model: 사용할 Anthropic 모델
            temperature: 창의성 조절 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            
        Returns:
            생성된 텍스트
        """
        if not self.anthropic_client:
            raise ValueError("Anthropic 클라이언트가 초기화되지 않았습니다.")
        
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="당신은 게임 기획 전문가입니다. 창의적이고 구체적인 게임 기획을 작성해 주세요.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic API 오류: {str(e)}")
            raise
    
    def generate_text(self, 
                     prompt: str,
                     provider: str = "openai",
                     model: str = None, 
                     temperature: float = 0.7,
                     max_tokens: int = 2000) -> str:
        """
        지정된 LLM 제공자를 사용하여 텍스트 생성
        
        Args:
            prompt: 텍스트 생성을 위한 프롬프트
            provider: 사용할 LLM 제공자 ('openai' 또는 'anthropic')
            model: 사용할 모델 (제공자에 따라 다름)
            temperature: 창의성 조절 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            
        Returns:
            생성된 텍스트
        """
        if provider.lower() == "openai":
            if model is None:
                model = "gpt-4-turbo"
            return self.generate_with_openai(prompt, model, temperature, max_tokens)
        
        elif provider.lower() == "anthropic":
            if model is None:
                model = "claude-3-opus-20240229"
            return self.generate_with_anthropic(prompt, model, temperature, max_tokens)
        
        else:
            raise ValueError(f"지원되지 않는 LLM 제공자: {provider}")
    
    def generate_structured_output(self, 
                                  prompt: str, 
                                  output_schema: Dict[str, Any],
                                  provider: str = "openai",
                                  model: str = None,
                                  temperature: float = 0.7) -> Dict[str, Any]:
        """
        구조화된 형식(JSON)으로 출력을 생성
        
        Args:
            prompt: 텍스트 생성을 위한 프롬프트
            output_schema: 예상되는 출력 스키마
            provider: 사용할 LLM 제공자
            model: 사용할 모델
            temperature: 창의성 조절 (0.0 ~ 1.0)
            
        Returns:
            구조화된 데이터 (Dict)
        """
        # 스키마를 프롬프트에 포함
        schema_str = json.dumps(output_schema, ensure_ascii=False, indent=2)
        structured_prompt = f"{prompt}\n\n다음 JSON 스키마에 맞게 응답해주세요:\n{schema_str}\n\n응답은 반드시 유효한 JSON 형식이어야 합니다."
        
        # 응답 생성
        response_text = self.generate_text(structured_prompt, provider, model, temperature)
        
        # JSON 추출 (응답에서 JSON만 파싱)
        try:
            # JSON 부분만 추출하는 로직
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # JSON을 찾을 수 없는 경우, 다시 시도
                clarification_prompt = f"이전 응답에서 유효한 JSON을 추출할 수 없습니다. 다음 스키마에 맞는 유효한 JSON만 응답해주세요:\n{schema_str}"
                retry_response = self.generate_text(clarification_prompt, provider, model, 0.1)  # 낮은 temperature로 정확성 향상
                
                json_start = retry_response.find('{')
                json_end = retry_response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = retry_response[json_start:json_end]
                    return json.loads(json_str)
                else:
                    raise ValueError("유효한 JSON 응답을 생성할 수 없습니다.")
                
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {str(e)}")
            print(f"원본 응답: {response_text}")
            raise ValueError("유효한 JSON 응답을 생성할 수 없습니다.")