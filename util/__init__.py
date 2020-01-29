from .bot import Bot
from .mongo import Mongo

async def setup(bot):
    await bot.add_cog(Util(bot))
