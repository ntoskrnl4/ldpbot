from client import client
import discord


@client.member_remove
async def ldp_exit_notification(member: discord.Member):
	if member.guild.id != 133083201458536448:
		return
	await client.get_channel(133083201458536448).send(f"> {member.mention} @{member.name}#{member.discriminator} has left the server")
