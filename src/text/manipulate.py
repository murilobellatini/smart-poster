def break_text(txt: str, word_count: int = 16):
    main_txt = ' '.join(txt.split(' ')[:word_count])
    caption = ''

    if word_count < len(txt.split(' ')):
        main_txt += ' ...'
        caption = '... ' + ' '.join(txt.split(' ')[word_count:])

    return main_txt, caption
