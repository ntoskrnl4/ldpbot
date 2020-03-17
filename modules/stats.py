from client import client
from datetime import datetime

import discord
import log
import os
import socket
import threading
import time

# Some optional things
try:
	import psutil
except ModuleNotFoundError:
	has_psutil = False
else:
	has_psutil = True

try:
	import pijuice
except ModuleNotFoundError:
	has_pijuice = False
except Exception as e:
	log.warn("Unexpected exception trying to import module pijuice", include_exception=True)
	has_pijuice = False
else:
	has_pijuice = True
	_iface = pijuice.PiJuiceInterface()  # Create the interface that we'll create the battery object with
	battery = pijuice.PiJuiceStatus(_iface)

client.basic_help(title="stats", desc=f"shows various running statistics of {client.bot_name}")

detailed_help = {
	"Usage": f"{client.default_prefix}stats",
	"Description": f"This command shows different available statistics of {client.bot_name}, including servers, uptime, and commands run.",
	"Related": f"`{client.default_prefix}info` - shows information about {client.bot_name}",
}
client.long_help(cmd="stats", mapping=detailed_help)


@client.ready
async def readier():
	def psutil_update_thread_loop(client):
		while client.active:
			# self_process.cpu_percent()  # not sure how to optimize this loop in another thread so we're going to comment it out and deal with it for now
			psutil.cpu_percent(percpu=True)
			time.sleep(5)

	global psutil_update_thread
	psutil_update_thread = threading.Thread(target=psutil_update_thread_loop, name="PSUtil_Background_Loop", args=[client])

	return


@client.command(trigger="stats", aliases=["statistics", "s", "status"])
async def statistics(command: str, message: discord.Message):
	if "--uptime" in command:
		up = time.perf_counter() - client.first_execution
		await message.channel.send(f"Uptime:\n`{up:.3f}` seconds\n`{up/86400:.4f}` days")
		return

	async with message.channel.typing():

		embed = discord.Embed(title=f"Running statistics for {client.bot_name}", description=discord.Embed.Empty, color=0x404040)

		up = time.perf_counter() - client.first_execution
		embed = embed.add_field(name="Uptime", value=f"{up:.3f} seconds\n{up/86400:.4f} days")
		embed = embed.add_field(name="Servers", value=len(client.guilds))
		embed = embed.add_field(name="Commands since boot", value=client.command_count)
		embed = embed.add_field(name="Messages since boot", value=client.message_count)
		n_connected = len(client.voice_clients)
		n_playing = len([x for x in client.voice_clients if x.is_playing()])
		embed = embed.add_field(name="Connected voice chats", value=f"{n_connected} ({n_playing} playing)")
		embed = embed.add_field(name="Bot Process ID", value=os.getpid())
		embed = embed.add_field(name="Host Machine Name", value=socket.gethostname())

		if has_pijuice:
			result = battery.GetChargeLevel()
			if result["error"] == "NO_ERROR":
				charge_level = f"{result['data']}%"
			else:
				charge_level = f"Error"

			result = battery.GetBatteryVoltage()
			if result["error"] == "NO_ERROR":
				charge_voltage = f"{result['data']/1000}v"
			else:
				charge_voltage = "Voltage unknown"

			battery_text = f"{charge_level} ({charge_voltage})\n"

			result = battery.GetStatus()
			if result['error'] == "NO_ERROR":
				if "CHARGING" in result['data']['battery']:
					battery_text += "Connected to mains"
				else:
					battery_text += "Running off battery"
			else:
				battery_text += "Unable to get status"

			embed = embed.add_field(name="Battery status", value=battery_text)

		if has_psutil:
			try:
				temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
			except (AttributeError, KeyError):
				temp = None
			self = psutil.Process()
			cpu_self = self.cpu_percent(interval=1)
			self_m_used = self.memory_info().rss
			m_raw = psutil.virtual_memory()
			m_total = m_raw.total
			m_available = m_raw.available
			m_used = m_total - m_available
			cpu = psutil.cpu_percent(percpu=True)
			index = 0
			cpu_text = ""
			for v in cpu:
				cpu_text += f"**CPU {index}:** {v}%\n"
				index += 1

			embed = embed.add_field(name="Host CPU temp", value=f"{int(temp) if temp is not None else 'Unknown'}°C")
			embed = embed.add_field(name="Process Memory", value=f"{self_m_used/(1024*1024):.3f} MiB")
			embed = embed.add_field(name="Process CPU", value=f"{cpu_self:.1f}%")
			embed = embed.add_field(name="System RAM Usage", value=f"{m_used/(1024*1024):.1f}/{m_total/(1024*1024):.1f} MiB ({(m_used/m_total)*100:.2f}%)")
			embed = embed.add_field(name="System CPU", value=cpu_text, inline=False)

		embed = embed.set_footer(text=datetime.utcnow().__str__())
	await message.channel.send(embed=embed)

