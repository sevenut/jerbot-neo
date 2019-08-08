import os
import re
import yaml
from datetime import timedelta
from discord import Embed, channel, member, message
from discord.ext import commands

bot = commands.Bot(command_prefix="!")
config = {}
# TODO aliases were never fully implemented in jerbot2, figure this out


def list_prettyprint(old_list: list):
    """
    Prepares a list for easier viewing on Discord.
    Example:
        list_prettyprint([foo, bar])
    Returns:
        `foo, bar`
    """
    return f'`{", ".join(old_list)}`'


def load_config():
    successful = []
    with open('config.yaml') as cfg:
        try:
            config['main'] = yaml.safe_load(cfg)
            successful.append('main')
        except Exception as e:
            print(f'Failed to load main configuration. ({e})')

    for name in os.listdir('config'):
        if name.startswith('config') and name.endswith('yaml'):
            server_id = re.sub(r'\D', '', name)
            with open('config/' + name) as cfg:
                try:
                    config[server_id] = yaml.safe_load(cfg)
                    successful.append(server_id)
                except Exception as e:
                    print('Failed to load {name}. ({e})')
    return successful


def load_modules():
    successful = []
    for extension in sorted(config['main']['extensions']):
        try:
            bot.load_extension(f'modules.{extension}')
            successful.append(extension)
        except Exception as e:
            print(f'Failed to load {extension}. ({e})')
    return successful


async def write_embed(channel: channel, member: member, color, title, event='', avatar=True, footer=None, fields=None,
                      message=None, description=None):
    """
    :param channel: ID of the channel to send the log embed in.
    :param member: Member that is being referenced in this embed.
    :param color: Color of the embed.
    :param title: Title of the embed.
    :param event: Event that is triggering the embed write: Member Joined, Member Left, Member Banned, etc. Optional.
    :param avatar: If avatar should be displayed in moderation logs. Default: True
    :param fields: Optional. [[title, content]]
    :param footer: Optional. Footer for the embed.
    :param message: Optional. Message string to send alongside the embed.
    :param message: Optional. Description of the embed.
    """
    if fields is None:
        fields = []
    embed = Embed(color=color, title=title, description=description)
    embed.set_author(name=event)
    if avatar:
        embed.set_thumbnail(url=member.avatar_url if member.avatar_url else member.default_avatar_url)
    if fields:
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=True)
    if footer:
        embed.set_footer(text=footer)
    await bot.get_channel(channel).send(message, embed=embed)

async def write_message(channel: channel, message: message):
    """
    :param channel: ID of the channel to send a message in.
    :param message: Message to send.
    """
    await bot.get_channel(channel).send(message)


async def check_roles(command: str, ctx):
    """
    Custom check. Checks if a the user has a role for the command in the config.
    :param command: Category in the YAML to look under
    :param ctx: discord.py context
    :return: boolean
    """
    for role in ctx.message.author.roles:
        if role.name.lower() in {i.lower() for i in config[str(ctx.guild.id)][command]['roles']}:
            return True
    return False


async def module_enabled(command: str, id: int or str):
    """
    Custom check. Checks if the module is enabled for the server in the config.
    :param command: Category in the YAML to look under
    :param id: server ID
    :return: boolean
    """
    return config[str(id)][command]['enabled']

async def parse_time(time: str):
    """
    Takes an input String and parses it into a usable timedelta.
    :param parsestring: Input string
    :return: timedelta
    """
    case = dict(d=timedelta(days=int(re.sub(r'\D', '', time))), h=timedelta(hours=int(re.sub(r'\D', '', time))),
                m=timedelta(minutes=int(re.sub(r'\D', '', time))),
                s=timedelta(seconds=int(re.sub(r'\D', '', time))))
    return case.get(time[-1])
