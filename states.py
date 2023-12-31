from aiogram.fsm.state import State, StatesGroup

class RideBookingStates(StatesGroup):
    REQUEST_START = State()
    REQUEST_DESTINATION = State()

class RatingStates(StatesGroup):
    RATING = State()
    REVIEW = State()

class RegistrationStates(StatesGroup):
    START = State()
    NAME = State()
    PHONE = State()
    ROLE = State()
    PROFILE_EDIT = State()
    LOCATION = State()
    DESTINATION = State()