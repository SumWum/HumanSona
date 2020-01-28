def strikethrough(text):
    return "~~{}~~".format(text)


def underline(text):
    return "__{}__".format(text)


def error(text):
    return "\N{NO ENTRY SIGN} {}".format(text)


def warning(text):
    return "\N{WARNING SIGN} {}".format(text)


def info(text):
    return "\N{INFORMATION SOURCE} {}".format(text)


def question(text):
    return "\N{BLACK QUESTION MARK ORNAMENT} {}".format(text)


def bold(text):
    return "**{}**".format(text)


def box(text, lang=""):
    ret = "```{}\n{}\n```".format(lang, text)
    return ret


def inline(text):
    return "`{}`".format(text)


def italics(text):
    return "*{}*".format(text)
