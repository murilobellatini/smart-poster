from src.content.produce import ContentProducer

if __name__ == "__main__":
    cp = ContentProducer(
        themes=['tolkien', 'harry potter', 'dungeons', 'shakespeare'],
        posts_per_theme=3,
    )
    cp.produce_content()
