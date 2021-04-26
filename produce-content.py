from src.content.produce import ContentProducer
cp = ContentProducer(
    themes=['sports', 'arts', 'drawing'],
    posts_per_theme=10,
)
cp.produce_content()
