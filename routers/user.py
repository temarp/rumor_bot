from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from texts import text
from database import requests as rq
from keyboard import inline_kb as in_kb
from keyboard import reply_kb as reply_kb
from states import RoadChoose, PodrazdChoose

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=text.START, reply_markup=reply_kb.reply_menu_kb)

    await message.answer('Как вы хотите выбрать мероприятие?\n\n'
                         '<b>Дорога</b> - фильтрация мероприятий по дорогам\n\n'
                         '<b>Подразделение</b> - фильтрация мероприятий по дорогам', reply_markup=in_kb.choose_filter)


@router.callback_query(F.data == 'road')
async def start_road(call: CallbackQuery, state: FSMContext):
    await state.clear()
    level = await rq.get_level_road()

    await call.message.edit_text('<b>Выберите уровень совета!</b>', reply_markup=await in_kb.kb_level(level))
    await state.set_state(RoadChoose.lvl)


@router.callback_query(RoadChoose.lvl, F.data.startswith('lvl_'))
async def choose_level_road(call: CallbackQuery, state: FSMContext):
    lvl = call.data.split('_')[-1]
    await state.update_data(lvl=lvl)
    await call.message.edit_text(text='<b>Выберите название дороги</b>', reply_markup=await in_kb.kb_road_name(0, level=lvl))
    await state.set_state(RoadChoose.name)

@router.callback_query(F.data == 'back_choose')
async def back_choose(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text='Как вы хотите выбрать мероприятие?\n\n'
                         '<b>Дорога</b> - фильтрация мероприятий по дорогам\n\n'
                         '<b>Подразделение</b> - фильтрация мероприятий по дорогам', reply_markup=in_kb.choose_filter)


@router.callback_query(RoadChoose.name, F.data.startswith('page_road_'))
async def choose_name_road(call: CallbackQuery, state: FSMContext):
    lvl = (await state.get_data())['lvl']
    index = int(call.data.split('_')[-1])
    await call.message.edit_text(text='<b>Выберите название дороги</b>', reply_markup=await in_kb.kb_road_name(index, level=lvl))


@router.callback_query(RoadChoose.name, F.data.startswith('road_name_'))
async def update_road(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    name = call.data.split('_')[-1]
    await rq.add_road(name=name, level=data['lvl'], tg_id=call.from_user.id)
    await call.message.edit_text('Я запомнил вашу дорогу!')

@router.callback_query(F.data == 'podrazd')
async def start_choose_podrazd(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PodrazdChoose.reqion)
    await call.message.edit_text('Выберите свой регион!', reply_markup=await in_kb.kb_region(0))

@router.callback_query(PodrazdChoose.reqion, F.data.startswith('page_region_'))
async def choose_region(call: CallbackQuery, state: FSMContext):
    index = int(call.data.split('_')[-1])
    await call.message.edit_text('Выберите свой регион!', reply_markup=await in_kb.kb_region(index))

@router.callback_query(PodrazdChoose.reqion, F.data.startswith('region_name_'))
async def choose_name_podrazd(call: CallbackQuery, state: FSMContext):
    name_podrazd = call.data.split('_')[-1]
    text_, kb = await in_kb.kb_name_podrazd(0, name_podrazd)
    await state.update_data(name_podrazd=name_podrazd)
    await state.set_state(PodrazdChoose.name)
    await call.message.edit_text('Теперь аыберите свое подразделение, нажав на кнопку с той цифрой, '
                                 'которой соответствует ваше подразделение\n\n'
                                 f'{text_}', reply_markup=kb)


@router.callback_query(PodrazdChoose.name, F.data.startswith('page_podrazd_'))
async def page_podrazd(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name_podr = data['name_podrazd']
    index = int(call.data.split('_')[-1])
    text_, kb = await in_kb.kb_name_podrazd(index, name_podr)
    await call.message.edit_text('Теперь выберите свое подразделение, нажав на кнопку с той цифрой, '
                                 'которой соответствует ваше подразделение\n\n'
                                 f'{text_}', reply_markup=kb)


@router.callback_query(PodrazdChoose.name, F.data.startswith('podrazd_name'))
async def update_name_podrazd(call: CallbackQuery, state: FSMContext):
    await state.clear()
    tg_id = call.from_user.id
    id_podr = int(call.data.split('_')[-1])

    await rq.add_podrazd(id_podrazd=id_podr, tg_id=tg_id)
    await call.message.edit_text('Ваш регион добавлен!')
