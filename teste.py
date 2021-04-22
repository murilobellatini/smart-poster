from src.text.extract import QuoteExtractor
from src.content.produce import Post
url = 'http://wallpoper.com/images/00/37/47/63/thor-marvel_00374763.jpg'
author = 'Thor'
profile = '@marvelnatics'
qe = QuoteExtractor('thor')
p = Post(quote=qe.results[0], img_url=url, profile_name=profile)
print(p.caption)
p.creative
