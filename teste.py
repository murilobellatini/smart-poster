from src.image.merge import Creative
txt = 'Prefiro ser um macaco sem cérebro do que um monstro sem coração.'
url = 'https://i.pinimg.com/564x/7b/eb/1f/7beb1f280483ed305fd44e3ced3cf752.jpg'
author = 'Son Goku'
profile = '@kamehameha'
c = Creative(txt=txt, img_url=url, bottom_right_txt=author,
             top_right_txt=profile)
c.creative
