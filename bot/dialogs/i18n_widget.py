from typing import Dict, List

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text
from fluentogram import TranslatorRunner


class I18NFormat(Text):
    def __init__(self, key: str, when: WhenCondition = None):
        super().__init__(when)
        self.key = key

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        i18n: TranslatorRunner = manager.middleware_data.get('i18n')
        value = i18n.get(self.key, **data)
        if value is None:
            raise KeyError(f'translation key = "{self.key}" not found')
        return value