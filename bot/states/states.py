from aiogram.fsm.state import StatesGroup, State


class Menu(StatesGroup):
    new = State()
    save = State()
    delete = State()


class Settings(StatesGroup):
    main = State()
    language = State()


class Knowledge(StatesGroup):
    main = State()
    add = State()
    add_not_format = State()
    add_approve = State()
    delete = State()
    delete_approve = State()


class Wallet(StatesGroup):
    main = State()
    balance = State()
    delete = State()
    balance_after_check = State()
    add_not_format = State()

class Input(StatesGroup):
    main = State()


class Balance(StatesGroup):
    main = State()
    choose = State()
    input = State()
    input_not_format = State()