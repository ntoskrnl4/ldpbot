from client import client
from key import whitelist_auth_users

import asyncio
import discord
import key
import subprocess


@client.command("whitelist", aliases=["wl"])
async def whitelist(command: str, message: discord.Message):
	if message.author.id not in whitelist_auth_users:
		await message.add_reaction("❌")
		return

	parts = command.split(" ")
	if len(parts) == 1:
		await message.channel.send("Argument error: Need name of user to whitelist")
		return

	new_user = parts[1]

	async with message.channel.typing():
		pc_proc = subprocess.Popen(f"python3.6 pyCraft/start.py -u {key.minecraft_username} -p {key.minecraft_password} -s LittleDigPlanet.beastmc.com:25587", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		# wait a bit before sending data to it
		await asyncio.sleep(10)
		pc_proc.communicate(input=(f"/whitelist add {new_user}\n").encode('utf-8'))
		await asyncio.sleep(2)
		stdout, stderr = pc_proc.communicate()
		pc_proc.terminate()
		await asyncio.sleep(2)
		pc_proc.kill()

	if "success" in stdout.decode().lower():
		await message.channel.send("Successfully added user to whitelist. If this did not work, please open the server console manually and try again.")
	else:
		await message.channel.send("Whitelist command sent, but did not receive confirmation of success. If whitelisting did fail, please open server console manually.")
	return
