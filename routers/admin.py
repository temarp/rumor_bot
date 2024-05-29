from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from texts import text
from database import requests as rq
from keyboard import inline_kb as in_kb
from states import RoadChoose, PodrazdChoose, AddEvent
from config import PASSWORD

admin_router = Router()


@admin_router.message(Command('add_event'))
async def input_password_event(mess: Message, state: FSMContext):
    await state.clear()

    await state.set_state(AddEvent.password)
    await mess.answer(text='Введите пароль, чтобы добавить мероприятие\n\n'
                           'Чтобы выйти из функции добавления - нажмите /start')

@admin_router.message(AddEvent.password)
async def check_password_event(mess: Message, state: FSMContext):
    if mess.text.lower() == PASSWORD:
        level = await rq.get_level_road()
        await mess.answer('Отличное!\n\nТеперь давайте выберем дорогу!\n\n'
                          '<b>Выберите совет</b>', reply_markup=await in_kb.kb_level_event(level))
        await state.set_state(AddEvent.lvl)
    else:
        await mess.answer(text='Неправильный пароль, повторите попытку\n\n'
                               'Чтобы выйти из функции добавления - нажмите /start')


@admin_router.callback_query(AddEvent.lvl)
async def choose_lvl_admin(call: CallbackQuery, state: FSMContext):
    lvl = call.data.split('_')[-1]
    await state.update_data(lvl=lvl)
    await call.message.edit_text(text='<b>Выберите название дороги</b>',
                                 reply_markup=await in_kb.kb_road_name(0, level=lvl))
    await state.set_state(AddEvent.road_name)


@admin_router.callback_query(AddEvent.road_name, F.data.startswith('page_road_'))
async def kb_name_road(call: CallbackQuery, state: FSMContext):
    lvl = (await state.get_data())['lvl']
    index = int(call.data.split('_')[-1])
    await call.message.edit_text(text='<b>Выберите название дороги</b>',
                                 reply_markup=await in_kb.kb_road_name(index, level=lvl))

@admin_router.callback_query(AddEvent.road_name, F.data.startswith('road_name_'))
async def choose_name_road_admin(call: CallbackQuery, state: FSMContext):
    await state.update_data(name_road=call.data.split('_')[-1])

    await call.message.edit_text('Выберите регион, в котором будет проходить мероприятие!',
                                 reply_markup=await in_kb.kb_region_event(0))
    await state.set_state(AddEvent.region)

@admin_router.callback_query(AddEvent.region, F.data.startswith('page_region_'))
async def choose_region_kb_admin(call: CallbackQuery, state: FSMContext):
    index = int(call.data.split('_')[-1])
    await call.message.edit_text('Выберите свой регион!', reply_markup=await in_kb.kb_region_event(index))


@admin_router.callback_query(AddEvent.region, F.data.startswith('region_name_'))
async def choose_name_region_event(call: CallbackQuery, state: FSMContext):
    name_region = call.data.split('_')[-1]
    text_, kb = await in_kb.kb_name_podrazd(0, name_region)
    await state.update_data(name_region=name_region)
    await state.set_state(AddEvent.name_podrazd)
    await call.message.edit_text('Теперь аыберите свое подразделение, нажав на кнопку с той цифрой, '
                                 'которой соответствует ваше подразделение\n\n'
                                 f'{text_}', reply_markup=kb)

@admin_router.callback_query(AddEvent.name_podrazd, F.data.startswith('page_podrazd_'))
async def choose_page_podrazd(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name_reg = data['name_region']
    index = int(call.data.split('_')[-1])
    text_, kb = await in_kb.kb_name_podrazd(index, name_reg)
    await call.message.edit_text('Теперь аыберите свое подразделение, нажав на кнопку с той цифрой, '
                                 'которой соответствует ваше подразделение\n\n'
                                 f'{text_}', reply_markup=kb)

@admin_router.callback_query(AddEvent.name_podrazd, F.data.startswith('podrazd_name_'))
async def choose_name_podrazd_event(call: CallbackQuery, state: FSMContext):
    await state.update_data(group_id=call.data.split('_')[-1])
    await state.set_state(AddEvent.short_name)
    await call.message.edit_text(text='Напишите короткое название для мероприятия')

@admin_router.message(AddEvent.short_name, F.text)
async def short_name_event(mess: Message, state: FSMContext):
    short_name = mess.text
    await state.update_data(short_name=short_name)
    await state.set_state(AddEvent.descr)
    await mess.answer(text='Введите описание мероприятия')

@admin_router.message(AddEvent.descr, F.text)
async def descr_name_event(mess: Message, state: FSMContext):
    descr = mess.html_text

    await state.update_data(descr=str(descr))
    await state.set_state(AddEvent.date_start)
    await mess.answer('<b>Введите дату мероприятия в формате: 2024-05-29 12:30</b>')

@admin_router.message(AddEvent.date_start, F.text)
async def date_start_event(mess: Message, state: FSMContext):
    date_start = mess.text
    format = '%Y-%m-%d %H:%M'
    try:
        date_start = datetime.strptime(date_start, format)
        await state.update_data(date_start=date_start)
        await state.set_state(AddEvent.photo)
        await mess.answer('Пришлите фотографию мероприятия')

    except:
        await mess.answer(text='Вы ввели дату в неправильном формате, повторите попытку')


@admin_router.message(AddEvent.photo, F.photo)
async def photo_event(mess: Message, state: FSMContext):
    photo_id = mess.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    data = (await state.get_data())
    date_st = data["date_start"]
    date_st = date_st.strftime(format='%Y-%m-%d %H:%M')
    caption = f'<b>{data["short_name"]}</b>\n\n{date_st}\n\n{data["descr"]}'
    await mess.answer('Мероприятие успешно добавлено!')
    await mess.answer_photo(photo=photo_id, caption=caption)
    await rq.add_event(name=data["short_name"], group_id=data['group_id'],
                       road_name=data['name_road'], picture=photo_id,
                       desc=data["descr"], date_start=data["date_start"])
    await state.clear()



