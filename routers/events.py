from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from texts import text
from database import requests as rq
from keyboard import inline_kb as in_kb
from keyboard import reply_kb as reply_kb
from states import RoadChoose, PodrazdChoose, MarkEvent, LastEvent


event_router = Router()


@event_router.message(F.text == 'Мои мероприятия')
async def get_my_events(mess: Message, state: FSMContext):
    await state.clear()
    user = await rq.check_user(mess.from_user.id)
    if not user:
        return await mess.answer('Вы не выбрали ни дорогу, ни подразделение\n\n'
                                 '<b>Нажмите кнопку</b> "Изменить дорогу/подразделение"')

    event, kb = await in_kb.my_events_kb(mess.from_user.id, 0)
    if not event:
        return await mess.answer(text='Вы не подписаны ни на одно мероприятие(')


    date_st = event[0].date_start
    date_st = date_st.strftime(format='%Y-%m-%d %H:%M')
    date_ = event[0].date_start
    marks = round(event[0].mark / event[0].count_mark, 1) if event[0].count_mark != 0 else 'нет'
    if date_ < datetime.now():
        text = f'<b>{event[0].name}\n\nОценка - {marks}</b>\n\n{date_st}\n\n{event[0].description}'
    else:
        text = f'<b>{event[0].name}</b>\n\n{date_st}\n\n{event[0].description}'

    await mess.answer_photo(photo=event[0].picture, caption=text, reply_markup=kb)

@event_router.callback_query(F.data.startswith('page_event_'))
async def page_events(call: CallbackQuery, state: FSMContext):
    await state.clear()
    index = int(call.data.split('_')[-1])
    event, kb = await in_kb.my_events_kb(call.from_user.id, index)
    date_st = event[0].date_start
    date_st = date_st.strftime(format='%Y-%m-%d %H:%M')
    date_ = event[0].date_start
    marks = round(event[0].mark / event[0].count_mark, 1) if event[0].count_mark != 0 else 'нет'
    if date_ < datetime.now():
        text = f'<b>{event[0].name}\n\nОценка - {marks}</b>\n\n{date_st}\n\n{event[0].description}'
    else:
        text = f'<b>{event[0].name}</b>\n\n{date_st}\n\n{event[0].description}'

    media = InputMediaPhoto(media=event[0].picture, caption=text)

    await call.message.edit_media(media=media, reply_markup=kb)


@event_router.message(F.text == 'Изменить дорогу/подразделение')
async def reply_update_road_podrazd(mess: Message, state: FSMContext):
    await state.clear()
    await mess.answer(
                         '<b>Дорога</b> - фильтрация мероприятий по дорогам\n\n'
                         '<b>Подразделение</b> - фильтрация мероприятий по дорогам', reply_markup=in_kb.choose_filter)

@event_router.callback_query(F.data.startswith('delete_event_'))
async def delete_event_user(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await rq.delete_event_from_user(call.data.split('_')[-1])
    await call.answer(text='Мероприятие удалено!', show_alert=True)


@event_router.callback_query(F.data.startswith('mark_event_'))
async def set_mark_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    check = await rq.check_mark_event_user(call.data.split('_')[-1])
    if not check:
        return await call.answer(text='Вы уже ставили оценку', show_alert=True)
    await state.set_state(MarkEvent.mark)
    await state.update_data(event_id=call.data.split('_')[-1])
    await call.message.answer(text='Введите оценку от 1 до 10')


@event_router.message(MarkEvent.mark, F.text)
async def set_mark(mess: Message, state: FSMContext):
    data = await state.get_data()
    if mess.text.isdigit():
        await rq.set_mark_event(event_id=data['event_id'], count=int(mess.text))
        await mess.answer(text='Оценка успешно поставлена!')
        await state.clear()
    else:
        await mess.answer('Введите число')


@event_router.message(F.text == 'Прошедшие мероприятия')
async def last_events(mess: Message, state: FSMContext):
    await state.clear()
    check = await rq.check_user(mess.from_user.id)

    if not check:
        return await mess.answer('Вы не выбрали ни дорогу, ни подразделение\n\n'
                                 '<b>Нажмите кнопку</b> "Изменить дорогу/подразделение"')

    road_id = check.road_id
    group_id = check.group_id
    event, kb = await in_kb.last_events_kb(index=0, road_id=road_id, group_id=group_id)
    if not event:
        return await mess.answer(text='Мероприятий на ваших дорогах и подразделениях нет')

    date_st = event.date_start
    date_st = date_st.strftime(format='%Y-%m-%d %H:%M')
    marks = round(event.mark / event.count_mark, 1) if event.count_mark != 0 else 'нет'

    text = f'<b>{event.name}\n\nОценка - {marks}</b>\n\n{date_st}\n\n{event.description}'

    await mess.answer_photo(photo=event.picture, caption=text, reply_markup=kb)

@event_router.callback_query(F.data.startswith('page_last_event_'))
async def page_last_event(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    index = data[3]
    road_id = int(data[4]) if data[4] != '0' else None
    group_id = int(data[5]) if data[5] != '0' else None

    event, kb = await in_kb.last_events_kb(index=int(index), road_id=road_id, group_id=group_id)

    date_st = event.date_start
    date_st = date_st.strftime(format='%Y-%m-%d %H:%M')

    marks = round(event.mark / event.count_mark, 1) if event.count_mark != 0 else 'нет'
    text = f'<b>{event.name}\n\nОценка - {marks}</b>\n\n{date_st}\n\n{event.description}'
    media = InputMediaPhoto(media=event.picture, caption=text)

    await call.message.edit_media(media=media, reply_markup=kb)


@event_router.message(F.text == 'Будущие мероприятия')
async def start_new_events(mess: Message, state: FSMContext):
    await state.clear()
    check = await rq.check_user(mess.from_user.id)

    if not check:
        return await mess.answer('Вы не выбрали ни дорогу, ни подразделение\n\n'
                                 '<b>Нажмите кнопку</b> "Изменить дорогу/подразделение"')

    road_id = check.road_id
    group_id = check.group_id
    print(road_id, group_id)
    event, kb = await in_kb.new_events_kb(index=0, road_id=road_id, group_id=group_id)
    if not event:
        return await mess.answer(text='Мероприятий на ваших дорогах и подразделениях нет')

    date_st = event.date_start
    date_st = date_st.strftime(format='%Y-%m-%d %H:%M')

    text = f'<b>{event.name}</b>\n\n{date_st}\n\n{event.description}'

    await mess.answer_photo(photo=event.picture, caption=text, reply_markup=kb)


@event_router.callback_query(F.data.startswith('page_new_event_'))
async def page_new_event(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    index = data[3]
    road_id = int(data[4]) if data[4] != '0' else None
    group_id = int(data[5]) if data[5] != '0' else None

    event, kb = await in_kb.new_events_kb(index=int(index), road_id=road_id, group_id=group_id)

    date_st = event.date_start
    date_st = date_st.strftime(format='%Y-%m-%d %H:%M')

    text = f'<b>{event.name}</b>\n\n{date_st}\n\n{event.description}'
    media = InputMediaPhoto(media=event.picture, caption=text)

    await call.message.edit_media(media=media, reply_markup=kb)

@event_router.callback_query(F.data.startswith('add_event_user_'))
async def add_event_notebook_user(call: CallbackQuery, state: FSMContext):
    event_id = int(call.data.split('_')[-1])
    check_add = await rq.add_event_notebook(event_id, call.from_user.id)
    if check_add:
        return await call.answer('Вы подписались на мероприятие', show_alert=True)

    return await call.answer('Вы уже подписаны на это мероприятие', show_alert=True)



