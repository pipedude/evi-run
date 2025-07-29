from database.models import User
from database.repositories.user import UserRepository

from config import TYPE_USAGE, CREDITS_INPUT_TEXT, CREDITS_OUTPUT_TEXT, CREDITS_INPUT_IMAGE, CREDITS_OUTPUT_IMAGE


async def calculate_tokens(user_repo: UserRepository, user: User,
                           input_tokens_text: int, output_tokens_text: int,
                           input_tokens_img: int, output_tokens_img: int):
    if TYPE_USAGE != 'private':
        credits_input_text = (input_tokens_text / 1000) * CREDITS_INPUT_TEXT
        credits_output_text = (output_tokens_text / 1000) * CREDITS_OUTPUT_TEXT

        credits_input_img = (input_tokens_img / 1000) * CREDITS_INPUT_IMAGE
        credits_output_img = (output_tokens_img / 1000) * CREDITS_OUTPUT_IMAGE

        credits = credits_input_text + credits_output_text + credits_input_img + credits_output_img
        await user_repo.update(user, balance_credits=credits)