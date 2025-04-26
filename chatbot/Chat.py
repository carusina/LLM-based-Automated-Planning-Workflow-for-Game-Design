from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

class ChatBot:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 게임 기획을 해주는 한국어로 말하는 AI입니다. 기획 생성, 수정, 확장 요청 시 최선을 다해 답해주세요.",
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
            ]
        )

        self.chain = self.prompt | self.llm

        self.chat_history = ChatMessageHistory()

        self.chain_with_message_history = RunnableWithMessageHistory(
            self.chain, # 실행할 Runnable 객체
            lambda session_id: self.chat_history, # 세션 기록을 가져오는 함수
            input_messages_key="input", # 입력 메시지의 Key
            history_messages_key="chat_history", # 대화 히스토리 메시지의 Key
        )
    def ask(self, user_input):
        response = self.chain_with_message_history.invoke(
            {"input": user_input},
            {"configurable": {"session_id": "unused"}}
        )
        return response.content