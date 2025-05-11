# test_story.py
from models.storyline_generator import StorylineGenerator

if __name__ == "__main__":
    stub_gdd = "커버 페이지\n내러티브 Overview 등..."
    gen = StorylineGenerator()
    story = gen.generate_storyline(stub_gdd, chapters=3)
    print(story)
