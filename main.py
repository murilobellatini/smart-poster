from src.content.produce import ContentProducer

if __name__ == "__main__":
    cp = ContentProducer(
        themes=['wrong',
                # 'green', 'purple'
                ],
        posts_per_theme=1,
    )
    cp.produce_content()
