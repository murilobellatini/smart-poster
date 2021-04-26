from src.content.produce import ContentProducer

if __name__ == "__main__":
    cp = ContentProducer(
        themes=['technology',
                ],
        posts_per_theme=5,
    )
    cp.produce_content()
