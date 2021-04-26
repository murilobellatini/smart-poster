from src.content.produce import ContentProducer

if __name__ == "__main__":
    cp = ContentProducer(
        themes=['right',
                'green',
                'purple',
                'wrong',
                ],
        posts_per_theme=5,
    )
    cp.produce_content()
