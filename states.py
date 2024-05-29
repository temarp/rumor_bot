from aiogram.fsm.state import State, StatesGroup

class RoadChoose(StatesGroup):
    lvl = State()
    name = State()

class PodrazdChoose(StatesGroup):
    reqion = State()
    name = State()

class AddEvent(StatesGroup):
    password = State()
    lvl = State()
    road_name = State()
    region = State()
    name_podrazd = State()
    short_name = State()
    descr = State()
    photo = State()
    date_start = State()

class MarkEvent(StatesGroup):
    mark = State()

class LastEvent(StatesGroup):
    event = State()