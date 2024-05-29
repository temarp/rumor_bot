import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from database.models import async_main
from routers.user import router
from routers.admin import admin_router
from routers.events import event_router
from commands import set_commands

bot = Bot(TOKEN, parse_mode='HTML')

dp = Dispatcher()




async def main():
    dp.include_router(router)
    dp.include_router(admin_router)
    dp.include_router(event_router)
    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)

    await async_main()
    await dp.start_polling(bot)

async def on_startup(bot: Bot):
    await set_commands(bot)





if __name__ == '__main__':
    asyncio.run(main())