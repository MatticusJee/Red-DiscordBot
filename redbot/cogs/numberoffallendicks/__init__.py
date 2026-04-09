from redbot.core.bot import Red
from .numberoffallendicks import FallenDicksCounter


async def setup(bot: Red):
    """Load the FallenDicksCounter cog."""
    await bot.add_cog(FallenDicksCounter(bot))
