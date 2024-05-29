import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import requests as rq

choose_filter = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Дорога', callback_data='road')],
        [InlineKeyboardButton(text='Подразделение', callback_data='podrazd')],

    ]
)

async def kb_level_event(levels: list):
    builder = InlineKeyboardBuilder()
    lvl_sp = [InlineKeyboardButton(text=i, callback_data=f'lvl_{i}') for i in levels]

    builder.add(*lvl_sp)
    return builder.adjust(1).as_markup()


async def kb_level(levels: list):
    builder = InlineKeyboardBuilder()
    lvl_sp = [InlineKeyboardButton(text=i, callback_data=f'lvl_{i}') for i in levels]

    builder.add(*lvl_sp)
    builder.row(InlineKeyboardButton(text='Назад 🔙', callback_data='back_choose'), width=1)

    return builder.adjust(1).as_markup()


async def kb_region_event(index):
    builder = InlineKeyboardBuilder()
    regions = await rq.get_regions()
    regions = [regions[i:i + 10] for i in range(0, len(regions), 10)]

    sp_buttons = []

    for region in regions[index]:
        sp_buttons.append(InlineKeyboardButton(text=region, callback_data=f'region_name_{region}'))
    builder.row(*sp_buttons, width=2)

    if index == 0 and len(regions) == 1:
        return builder.as_markup()

    elif index == 0 and len(regions) != 1:
        builder.row(InlineKeyboardButton(text='⏭', callback_data=f'page_region_{index + 1}'))
        return builder.as_markup()

    elif index + 1 == len(regions):
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_region_{index - 1}'))
        return builder.as_markup()
    else:
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_region_{index - 1}'),
                    InlineKeyboardButton(text='⏭', callback_data=f'page_region_{index + 1}'), width=2)
        return builder.as_markup()


async def kb_region(index):
    builder = InlineKeyboardBuilder()
    regions = await rq.get_regions()
    regions = [regions[i:i + 10] for i in range(0, len(regions), 10)]

    sp_buttons = []

    for region in regions[index]:
        sp_buttons.append(InlineKeyboardButton(text=region, callback_data=f'region_name_{region}'))
    builder.row(*sp_buttons, width=2)

    if index == 0 and len(regions) == 1:
        builder.row(InlineKeyboardButton(text='Назад 🔙', callback_data='back_choose'), width=1)
        return builder.as_markup()

    elif index == 0 and len(regions) != 1:
        builder.row(InlineKeyboardButton(text='⏭', callback_data=f'page_region_{index + 1}'))
        builder.row(InlineKeyboardButton(text='Назад 🔙', callback_data='back_choose'), width=1)
        return builder.as_markup()

    elif index + 1 == len(regions):
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_region_{index - 1}'))
        builder.row(InlineKeyboardButton(text='Назад 🔙', callback_data='back_choose'), width=1)
        return builder.as_markup()
    else:
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_region_{index - 1}'),
                    InlineKeyboardButton(text='⏭', callback_data=f'page_region_{index + 1}'), width=2)
        builder.row(InlineKeyboardButton(text='Назад 🔙', callback_data='back_choose'), width=1)
        return builder.as_markup()


async def kb_name_podrazd(index, region):
    builder = InlineKeyboardBuilder()
    names = await rq.get_names_podrazd(region)
    names = [names[i:i + 5] for i in range(0, len(names), 5)]

    text = ''
    sp_buttons = []

    for num, name in enumerate(names[index], 1):
        sp_buttons.append(InlineKeyboardButton(text=str(name.id), callback_data=f'podrazd_name_{name.id}'))
        text = text + f'{name.id} - {name.podrazd.replace(r'\xa0', '')}\n\n'
    builder.row(*sp_buttons, width=2)

    if index == 0 and len(names) == 1:
        return text, builder.as_markup()

    elif index == 0 and len(names) != 1:
        builder.row(InlineKeyboardButton(text='⏭', callback_data=f'page_podrazd_{index + 1}'))
        return text, builder.as_markup()

    elif index + 1 == len(names):
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_podrazd_{index - 1}'))
        return text, builder.as_markup()
    else:
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_podrazd_{index - 1}'),
                    InlineKeyboardButton(text='⏭', callback_data=f'page_podrazd_{index + 1}'), width=2)
        return text, builder.as_markup()



async def kb_road_name(index, level):
    builder = InlineKeyboardBuilder()
    roads = await rq.get_name_road(level)
    roads = [roads[i:i + 5] for i in range(0, len(roads), 5)]
    sp_buttons = []

    for road in roads[index]:
        sp_buttons.append(InlineKeyboardButton(text=road, callback_data=f'road_name_{road}'))
    builder.row(*sp_buttons, width=1)

    if index == 0 and len(roads) == 1:
        return builder.as_markup()

    elif index == 0 and len(roads) != 1:
        builder.row(InlineKeyboardButton(text='⏭', callback_data=f'page_road_{index + 1}'))
        return builder.as_markup()

    elif index + 1 == len(roads):
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_road_{index - 1}'))
        return builder.as_markup()
    else:
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_road_{index - 1}'),
                    InlineKeyboardButton(text='⏭', callback_data=f'page_road_{index + 1}'), width=2)
        return builder.as_markup()


async def my_events_kb(tg_id, index):
    builder = InlineKeyboardBuilder()
    events = await rq.get_events_user(tg_id)
    if len(events) == 0:
        return False, False

    date_ = events[index][0].date_start

    if date_ < datetime.datetime.now():
        builder.row(InlineKeyboardButton(text='Оценить', callback_data=f'mark_event_{events[index][0].id}'),
                    width=1)
    else:
        builder.row(InlineKeyboardButton(text='Отменить', callback_data=f'delete_event_{events[index][0].id}'),
                    width=1)


    if index == 0 and len(events) == 1:
        builder.row(InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'), width=1)
        return events[index], builder.as_markup()

    elif index == 0 and len(events) != 1:
        builder.row(InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'),
                    InlineKeyboardButton(text='⏭', callback_data=f'page_event_{index + 1}'),
                    width=2)
        return events[index], builder.as_markup()

    elif index + 1 == len(events):
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_event_{index - 1}'),
                    InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'), width=2)
        return events[index], builder.as_markup()

    else:
        builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_event_{index - 1}'),
                    InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'),
                    InlineKeyboardButton(text='⏭', callback_data=f'page_event_{index + 1}'), width=3)
        return events[index], builder.as_markup()


async def last_events_kb(index, road_id=None, group_id=None):
    builder = InlineKeyboardBuilder()
    events = await rq.get_last_events(road_id, group_id)
    events = [i[0] for i in events if i[0].date_start < datetime.datetime.now()]

    if len(events) == 0:
        return False, False
    date_ = events[index].date_start

    if date_ < datetime.datetime.now():

        if index == 0 and len(events) == 1:
            builder.row(InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'), width=1)

            return events[index], builder.as_markup()

        elif index == 0 and len(events) != 1:
            builder.row(InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'),
                        InlineKeyboardButton(text='⏭', callback_data=f'page_last_event_{index + 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'), width=2)
            return events[index], builder.as_markup()

        elif index + 1 == len(events):
            builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_last_event_{index - 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'),
                        InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'), width=2)
            return events[index], builder.as_markup()
        else:
            builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_last_event_{index - 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'),
                        InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'),
                        InlineKeyboardButton(text='⏭', callback_data=f'page_last_event_{index + 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'), width=3)
            return events[index], builder.as_markup()
    return False, False


async def new_events_kb(index, road_id=None, group_id=None):
    builder = InlineKeyboardBuilder()
    events = await rq.get_new_events(road_id, group_id)
    events = [i[0] for i in events if i[0].date_start > datetime.datetime.now()]
    print(events)
    if len(events) == 0:
        return False, False

    date_ = events[index].date_start
    print(date_)
    if date_ > datetime.datetime.now():
        builder.row(InlineKeyboardButton(text='✅Я пойду!', callback_data=f'add_event_user_{events[index].id}'), width=1)


        if index == 0 and len(events) == 1:
            builder.row(InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'), width=1)

            return events[index], builder.as_markup()

        elif index == 0 and len(events) != 1:
            builder.row(InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'),
                        InlineKeyboardButton(text='⏭', callback_data=f'page_new_event_{index + 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'), width=2)
            return events[index], builder.as_markup()

        elif index + 1 == len(events):
            builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_new_event_{index - 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'),
                        InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'), width=2)
            return events[index], builder.as_markup()
        else:
            builder.row(InlineKeyboardButton(text='⏮', callback_data=f'page_new_event_{index - 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'),
                        InlineKeyboardButton(text=f'{index + 1}/{len(events)}', callback_data='count'),
                        InlineKeyboardButton(text='⏭', callback_data=f'page_new_event_{index + 1}_{road_id if road_id else 0}_{group_id if group_id else 0}'), width=3)
            return events[index], builder.as_markup()
    return False, False

