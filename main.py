import argparse
from src.content.produce import ContentProducer

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Script for generating posts automatically based on a focal theme')

    parser.add_argument('-t', '--themes', type=str, required=True,
                        help='String of themes to generate the posts about; Enter multiple themes separating by comma `,`')

    parser.add_argument('-c', '--post_count_per_theme', type=int, required=True,
                        help='Amount of posts per theme')

    args = parser.parse_args()

    cp = ContentProducer(
        themes=args.themes.split(','),
        posts_per_theme=args.post_count_per_theme,
    )
    cp.produce_content()
