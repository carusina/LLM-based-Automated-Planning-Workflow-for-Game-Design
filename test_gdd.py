# test_gdd.py
from models.game_design_generator import GameDesignGenerator

if __name__ == "__main__":
    gen = GameDesignGenerator()
    # 실제 호출 전에 먼저 더미 LLM을 주입해도 좋습니다.
    gdd = gen.generate_gdd(
        idea="중세 판타지 모험",
        genre="액션 RPG",
        target="10~20대",
        concept="잃어버린 왕국을 되찾기 위한 여정"
    )
    print(gdd[:500])  # 앞 500자만 확인
