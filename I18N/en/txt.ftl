start_text = 
    I'm Evi — a practicing tech witch... haha, actually I'm a multi-agent system with artificial intelligence and I know practically everything about this... and other worlds! 😈✨

    I can complete various tasks and assignments for you, or we can just have fun chatting. 🦄👻

    My capabilities include (but are not limited to):
    - solving complex, multi-step tasks;
    - conducting deep research;
    - intelligent web search;
    - document and image analysis;
    - image creation;
    - DEX analytics and Solana token swapping.

    I can schedule task execution for the time you need or with a specific frequency. I have customizable memory and I remember important information from our conversations. You can also delete the history of our conversations or add new knowledge to my memory. 🧙‍♀️🔮

    Just write your requests in chat in natural language or send voice messages to start interacting! 🪄✨

    ⚠️ Tip! Periodically reset the conversation context with the /new command — this will help save tokens and speed up request processing.

close_kb = Close

command_new_text = Confirm starting a new dialog without saving the current one. It is recommended to complete the current task before starting a new dialog! After deletion, the current history will be erased and the context will be reset.

command_approve_new_text = Current dialog deleted!

command_new_approve_kb = Confirm

command_new_save_kb = Save dialog

command_save_text = Confirm saving the current dialog to memory. It is recommended to complete the current task before saving! After saving, a new dialog will start with reset context, but key moments from the current conversation will remain in the system memory.

command_save_approve_kb = Current dialog saved to system memory!

command_delete_text = Confirm deletion of the current dialog and all system memory about you.

command_delete_approve_text = System memory about you and dialog deleted! Start a new dialog.

token_price_error_text = Wrong format, example: 0.01

not_token_price_error_text = You haven't set the token price yet!

token_price_updated_text = Token price updated!

command_wallet_text = 
    If you already have a linked wallet, entering a new private key will replace it. Enter the Solana wallet private key in format [45, 456, …].

    Warning: use a separate wallet with a small balance, as the trading agent works in test mode!

cmd_help_text = 
    Interact with the system through the chat window. All functions are available through regular messages. Use Menu for additional parameter settings.

command_settings_text = Settings

settings_language_text = Interface language

text_choose_lang = Choose interface language:

back_kb = Back

text_document_upload = File successfully uploaded! You can ask a question.

command_knowledge_text = This is the system's general knowledge base. Added information will be available to all users (when using modes: free and pay)! Do you want to add files or clear the knowledge base?

command_knowledge_add_kb = Add information

command_knowledge_delete_kb = Clear knowledge base

command_knowledge_add_text = Send a text file with information to the chat! Add only one file at a time to the chat!

text_not_format_file = Wrong format, please try again! Supported document formats: .pdf, .txt, .md, .doc(x), .pptx and .py

text_approve_file = File successfully uploaded! You can ask a question.

command_knowledge_delete_text = Confirm deletion of the knowledge base.

text_approve_delete = Knowledge base deleted. Add new information to the knowledge base.

warning_save_context_txt = Error saving context to txt file!

warning_text_no_credits = Insufficient credits!

wait_answer_text = One moment ✨

answer_md = Download answer

warning_text_tokens = Dialog size exceeds 15,000 tokens! To save resources, you can save the dialog to system memory or delete it through the menu after completing the current task.

warning_text_format = Wrong format!

warning_text_error = An error occurred!

cmd_wallet_text_start = 
    If you already have a linked wallet, entering a new private key will replace it. Enter the Solana wallet private key in format [45, 456, …].

    Warning: use a separate wallet with a small balance, as the trading agent works in test mode!

wallet_balance_kb = Wallet balance

wallet_delete_key = Delete private key

not_format_wallet_key = Wrong format! Write the Solana wallet private key in format [45, 456, …].

text_after_add_key =
    Agent gained access to the wallet.

    Wallet balance:


wallet_delete_key_text = Confirm deletion of the private key.

command_delete_key_approve_text = Private key deleted. Link a new wallet to use the trading agent.

text_balance_wallet = Wallet balance:

cmd_wallet_text = Your balance:

add_balance_kb = Top up balance

text_add_balance = Enter payment amount in $, whole number not less than $1.

text_add_balance_error = Please try again! Enter payment amount in $, whole number not less than $1.

choose_type_pay_text = Choose top-up method:

ton_type_kb = TON

sol_type_kb = Token (Solana)

error_create_payment = An error occurred while creating the payment. Please try later.

check_payment_kb = Check payment

text_payment_create =
    Make a payment for: <code>{ $sum }</code>
    Wallet: <code>{ $wallet }</code>

text_payment_create_sol =
    Make a payment for: <code>{ $sum }</code> tokens
    Wallet: <code>{ $wallet }</code>
    Token address: <code>{ $token }</code>

error_get_token_price = Token price not specified. Please specify token price /token_price.

wait_check_payment_text = Checking payment ⏳

check_payment_success_text = Payment completed successfully!

check_payment_error_text = Payment was not completed! Please try later.

warning_text_no_row_md = Context was deleted. Row not found in database.

text_user_upload_file = The user uploaded the { $filename } file to the tool search_conversation_memory

wait_answer_text_scheduler = Executing the scheduler's request ✨