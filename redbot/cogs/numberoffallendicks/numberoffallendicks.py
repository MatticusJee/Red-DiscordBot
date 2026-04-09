import re
import logging
import discord
from random import choice
from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import bold, humanize_number

log = logging.getLogger("red.fallendickscounter")


class FallenDicksCounter(commands.Cog):
    """Track how many times users claim their dick has fallen off."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9876543210, force_registration=True)
        self.config.register_global(counter_enabled=True)
        self.config.register_guild(user_counts={})

        # Pattern to match various ways of saying "my dick fell off"
        self.fallen_dick_patterns = re.compile(
            r"\b(?:my\s+)?(?:dick|cock|penis|member|dong|wiener|johnson|schlong|package|nuts?|balls?|testicles?|manhood|willy)"
            r"s?\b"
            r"\s+(?:has\s+|have\s+|had\s+|just\s+)?"
            r"(?:fell\s+off|fallen\s+off|dropped\s+off|came\s+off|detached|gone|is\s+off|was\s+off|falls?\s+off|falling\s+off)",
            re.IGNORECASE
        )

        self.funny_responses = [
            "{mention}! Your dick has fallen off **{count}** {time_word}. Maybe it's time to see a doctor, or at least get some duct tape.",
            "Alert! {mention}'s dick has fallen off again! That's **{count}** {time_word} now. At this point, it should come with a warning label.",
            "Oh look, {mention}'s dick fell off **{count}** {time_word} now. Should I start a GoFundMe for some superglue?",
            "{mention}, your dick has fallen off **{count}** {time_word}. I'm starting to think it's a feature, not a bug.",
            "Breaking news: {mention}'s dick has fallen off **{count}** {time_word}. Scientists are baffled, nobody is surprised.",
            "{mention}, your dick fell off again! That's **{count}** {time_word}. Maybe try saying please next time it reattaches.",
            "Well well well, {mention}'s dick has fallen off **{count}** {time_word} now. I'm not saying you should carry it around in a ziplock bag, but...",
            "{mention}'s dick has fallen off **{count}** {time_word}. At this point, it's basically a recurring subscription service.",
        ]

    async def red_delete_data_for_user(self, **kwargs):
        """Delete user data - required by Red-DiscordBot data handling"""
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and count fallen dick mentions."""
        if message.author.bot or not message.guild:
            return

        if not message.content:
            return

        if not await self.config.counter_enabled():
            return

        if self.fallen_dick_patterns.search(message.content):
            user_id = str(message.author.id)
            async with self.config.guild(message.guild).user_counts() as counts:
                counts[user_id] = counts.get(user_id, 0) + 1
                new_count = counts[user_id]

            log.info(
                f"Fallen dick count for user {user_id} ({message.author.name}) "
                f"in guild {message.guild.id}: {new_count}"
            )

            # Send a funny response
            mention = message.author.mention
            time_word = "time" if new_count == 1 else "times"
            response = choice(self.funny_responses).format(
                mention=mention, count=humanize_number(new_count), time_word=time_word
            )
            await message.reply(response, mention_author=False)

    @commands.command()
    @commands.guild_only()
    async def numberoffallendicks(self, ctx, member: discord.Member = None):
        """Check how many times a user said their dick fell off.

        Usage: [p]numberoffallendicks [@user]

        If no user is provided, shows your own count.
        """
        if member is None:
            member = ctx.author

        counts = await self.config.guild(ctx.guild).user_counts()
        count = counts.get(str(member.id), 0)

        if count == 0:
            await ctx.send(
                f"{member.mention} hasn't mentioned their dick falling off in this server. Yet."
            )
        else:
            time_word = "time" if count == 1 else "times"
            await ctx.send(
                f"{member.mention} has said their dick fell off {bold(humanize_number(count))} {time_word} in this server."
            )

    @commands.command()
    @commands.guild_only()
    async def fallendickleaderboard(self, ctx):
        """Show the leaderboard of fallen dick mentions."""
        counts = await self.config.guild(ctx.guild).user_counts()

        if not counts:
            await ctx.send("No one has mentioned their dick falling off yet.")
            return

        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        lines = []
        for i, (user_id, count) in enumerate(sorted_counts[:10], 1):
            member = ctx.guild.get_member(int(user_id))
            display_name = member.mention if member else f"<@{user_id}>"
            lines.append(f"{i}. {display_name}: {humanize_number(count)}")

        leaderboard_text = "\n".join(lines)
        await ctx.send(
            f"**Fallen Dick Leaderboard**\n{leaderboard_text}"
        )

    @commands.command()
    @commands.is_owner()
    async def togglefallendickcounter(self, ctx):
        """Toggle the fallen dick counter on/off."""
        current = await self.config.counter_enabled()
        await self.config.counter_enabled.set(not current)

        status = "enabled" if not current else "disabled"
        await ctx.send(f"Fallen dick counter is now {status}.")
