from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

from config import AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE, LANGUAGE_FALLBACKS

DIR_PATH = 'I18N'


def i18n_factory() -> TranslatorHub:
    translators = []
    for lang in AVAILABLE_LANGUAGES:
        translators.append(
            FluentTranslator(
                locale=lang,
                translator=FluentBundle.from_files(
                    locale=lang,
                    filenames=[f'{DIR_PATH}/{lang}/txt.ftl'],
                    use_isolating=False)
            )
        )
    
    return TranslatorHub(
        LANGUAGE_FALLBACKS,
        translators,
        root_locale=DEFAULT_LANGUAGE,
    )