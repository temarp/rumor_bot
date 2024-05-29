import asyncio
from datetime import datetime

from sqlalchemy import select, update, delete

import pandas as pd
from database.models import async_session, User, Event, Group, NoteBook, Road


# async def main():
#     df = pd.read_excel('Podrazd.xlsx')
#     df_road = pd.read_excel('road_new.xlsx')
#     async with async_session() as session:
#         for index, value in df.iterrows():
#             region = value['Регион'] if len(value['Регион']) > 2 else 'другое'
#             city = value['Город'] if len(value['Город']) > 2 else 'другое'
#             name = value['Наименование']
#
#             session.add(Group(region=region, city=city, podrazd=name))
#         for index, value in df_road.iterrows():
#             name = value['Название']
#             level = value['Уровень']
#
#             session.add(Road(name=name, level=level))
#
#         await session.commit()
#
#         a = list(await session.scalars(select(Group.region).group_by(Group.region)))



async def check_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            return user

        return False

async def get_level_road():
    async with async_session() as session:
        levels = (await session.scalars(select(Road.level))).fetchall()
        return list(set(levels))

async def get_name_road(level):
    async with async_session() as session:
        names = (await session.scalars(select(Road.name).where(Road.level == level))).fetchall()
        return names

async def get_regions():
    async with async_session() as session:
        regions = list(set((await session.scalars(select(Group.region))).fetchall()))
        return regions

async def get_names_podrazd(region):
    async with async_session() as session:
        names = list(set((await session.scalars(select(Group).where(Group.region == region))).fetchall()))
        return names

async def add_road(name, level, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            road_id = await session.scalar(select(Road.id).where(Road.name == name))
            print(road_id)
            session.add(User(tg_id=tg_id, road_id=road_id))
            await session.commit()
        else:
            road_id = await session.scalar(select(Road.id).where(Road.name == name))
            print(road_id)
            await session.execute(update(User).where(User.tg_id == tg_id).values(road_id=road_id))
            await session.commit()

async def add_podrazd(id_podrazd, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, group_id=id_podrazd))
            await session.commit()
        else:
            await session.execute(update(User).where(User.tg_id == tg_id).values(group_id=id_podrazd))
            await session.commit()

async def add_event(name, group_id, road_name, picture, desc, date_start):
    async with async_session() as session:
        road_id = await session.scalar(select(Road.id).where(Road.name == road_name))
        session.add(Event(name=name, group_id=int(group_id), road_id=int(road_id), picture=picture, description=desc,
                    date_start=date_start))
        await session.commit()

async def get_events_user(tg_id):
    async with async_session() as session:
        user_id = await session.scalar(select(User.id).where(User.tg_id == int(tg_id)))

        events = (await session.execute(select(Event).join(NoteBook).where(NoteBook.user_id == user_id))).fetchall()
        return events

async def check_mark_event_user(event_id):
    async with async_session() as session:
        event = await session.scalar(select(NoteBook.mark).where(NoteBook.event_id == int(event_id)))

        if event == 0:
            return True
        return False

async def set_mark_event(event_id, count):
    async with async_session() as session:
        await session.execute(update(Event).where(Event.id == int(event_id)).values(mark=Event.mark + count,
                                                                                    count_mark=Event.count_mark + 1))

        await session.execute(update(NoteBook).where(NoteBook.event_id == int(event_id)).values(mark=1))

        await session.commit()
async def delete_event_from_user(event_id):
    async with async_session() as session:
        await session.execute(delete(NoteBook).where(NoteBook.event_id == int(event_id)))
        await session.commit()

async def get_last_events(road_id=None, group_id=None):
    async with async_session() as session:
        if road_id and group_id:
            events = (await session.execute(select(Event).where(Event.group_id == int(group_id)))).fetchall()
            events.extend((await session.execute(select(Event).where(Event.road_id == int(road_id)))).fetchall())
        elif road_id:
            events = (
                await session.execute(select(Event).where(Event.road_id == road_id))).fetchall()
        else:
            events = (
                await session.execute(select(Event).where(Event.group_id == group_id))).fetchall()
        return events

async def get_new_events(road_id=None, group_id=None):
    async with async_session() as session:
        print(road_id, group_id)
        if road_id and group_id:
            events = (await session.execute(select(Event).where(Event.group_id == int(group_id)))).fetchall()
            events.extend((await session.execute(select(Event).where(Event.road_id == int(road_id)))).fetchall())
        elif road_id:
            events = (
                await session.execute(select(Event).where(Event.road_id == road_id))).fetchall()
        else:
            events = (
                await session.execute(select(Event).where(Event.group_id == group_id))).fetchall()
        return events


async def add_event_notebook(event_id, tg_id):
    async with async_session() as session:
        user = (await session.scalars(select(NoteBook).join(User).where(User.tg_id == tg_id))).all()
        all_id_event_user = [i.event_id for i in user]
        if event_id not in all_id_event_user:
            try:
                session.add(NoteBook(user_id=user[0].user_id, event_id=event_id))
            except:
                user_id = await session.scalar(select(User.id).where(User.tg_id == int(tg_id)))
                session.add(NoteBook(user_id=user_id, event_id=event_id))
            await session.commit()
            return True
        return False



