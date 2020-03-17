from client import client
from datetime import datetime
from key import shutdown_users
from socket import gethostname

import asyncio
import discord
import log
import os
import time


@client.command(trigger="kill", aliases=["exit"])
async def command(command: str, message: discord.Message):
	if message.author.id not in shutdown_users:
		await message.add_reaction("❌")
	else:
		parts = command.split(" ")
		try:
			target_pid = int(parts[2])
		except IndexError:
			target_pid = os.getpid()
		except ValueError:
			await message.channel.send("Invalid integer of PID to kill")
			return
		if target_pid == os.getpid():
			# double check we want to
			uptime = time.perf_counter() - client.first_execution
			m = await message.channel.send("Are you sure you want to shut down the bot?\n"
										f"Hostname: {gethostname()}\n"
										f"Uptime: {uptime/86400:.4f} days\n"
										f"To confirm shutdown, react to this message with ☑ in 30 seconds")
			await m.add_reaction("☑")

			def reaction_check(reaction, user):
				return (reaction.message.id == m.id and
						user.id == message.author.id and
						reaction.emoji == "☑")

			try:
				await client.wait_for("reaction_add", check=reaction_check, timeout=30)
			except asyncio.TimeoutError:
				await m.add_reaction("❌")
				await m.remove_reaction("☑", m.guild.me)
				await message.add_reaction("❌")
				await m.edit(content=m.content.replace("To confirm shutdown, react to this message with ☑ in 30 seconds", "Shutdown timed out. Deleting this message in 30 seconds."), delete_after=30)
				return
			else:
				client.active = False
				await m.delete()
				await message.add_reaction("☑")
				await message.channel.send("Shutting down bot...")
				await message.channel.send(f"Uptime: { time.perf_counter() - client.first_execution:.3f} seconds ({(time.perf_counter() - client.first_execution) / 86400:.3f} days)")
				await asyncio.sleep(0.1)  # give the above a chance to do its thing
				log.info(f"Bot shutdown initiated at {datetime.utcnow().__str__()} by {message.author.name}#{message.author.discriminator}")
				await client.do_shutdown()
	return
