from discord.ext import commands
import discord
from configparser import ConfigParser
import asyncio

config = ConfigParser(allow_no_value=True)
config.read('donatorConfig.ini')
discord_client = commands.Bot(command_prefix = config['Bot']['Bot_Prefix'])
discord_client.remove_command("help")



@discord_client.event
async def on_ready():
    print(f'\n\nLogged in as: {discord_client.user.name} - {discord_client.user.id}\nVersion: {discord.__version__}\n')
    await discord_client.change_presence(status=discord.Status.online, activity=discord.Game("Aye!"))

@discord_client.command()
async def kill(ctx):
    await ctx.send("I didn't even want to be here Natzu!")
    await discord_client.logout()

@discord_client.command()
async def help(ctx):
    desc = ("I am Happy the Exceed donation bot! Use me to create instances of volunteer requests. Create an instance "
    "by supplying a name and the amount of blocks you want to create. 1 block equals 5 bases.\n\nOnce you create your instance "
    "you can view the panel with a /view <instance> command. This will display the panel with corresponding reactions that users can "
    "click on. When a user clicks on the reaction, their discord name will be displayed on the panel. Only CoC Leaders can unregister "
    "a clan mates call.")
    embed = discord.Embed(title='Happy!', description= desc, color=0x8A2BE2)

    create = ("Command to create a new instance of a donate panel. The command takes two arguments "
    "a name, and a quantity. The name can be anything for example, the clan that is currently using it. Quantity is "
    "the ammount of blocks you would like to display. Please DO NOT use spaces between names.")
    embed.add_field(name="""/create <string> <int>""", value=create, inline=False)

    listt = ("Command to list already created instances.")
    embed.add_field(name="""/listing""", value=listt, inline=False)

    view = ("View an instance already create in active mode. A user simply clicks on the emoji to register for the block.")
    embed.add_field(name="""/view <instance>""", value=view, inline=False)

    delete = ("Delete an instance.")
    embed.add_field(name="""/delete <instance>""", value=delete, inline=False)

    clear = ("Clear an instance.")
    embed.add_field(name="""/clear <instance>""", value=clear, inline=False)

    example = ("----------------\nExamples")
    val = ("""/create "cwl zulu" 3 \n/view "cwl zulu" """)
    embed.add_field(name=example, value=val, inline=False)
    await ctx.send(embed = embed)





@discord_client.command()
async def create(ctx, name, block):
    if authorized(ctx.message.author.roles):
        if block.isdigit():
            name = name.upper()
            lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

            config.set('instances', name)
            config.add_section(name)
            config.set(name, "instance_name", name)
            config.set(name, "blocks", block)
            
            for blk in range(0, int(block)):
                config.set(name, lister[blk], '')
            config.set(name, "topoff", '')

            with open('donatorConfig.ini', 'w') as f:
                config.write(f)

            await ctx.send(f"All set! Use /view {name} to activate your panel.")
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")

@create.error
async def create_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))


@discord_client.command()
async def listing(ctx):
    await ctx.send(embed = discord.Embed(title="**Instances:**", color=0x8A2BE2))
    for instance in config['instances']:
        await ctx.send(f"```{'':>6}{instance}```")

@discord_client.command()
async def delete(ctx, instance):
    instance = instance.upper()
    if authorized(ctx.message.author.roles):
        if instance in config['instances']:
            config['instances'].pop(instance)
            config.pop(instance)
            with open('donatorConfig.ini', 'w') as f:
                config.write(f)
            
            await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")
        else:
            await ctx.send(f"Did not find {instance}. Please make sure you have used quotes or match case. Copy+Past from /list_int")
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")

@delete.error
async def delete_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def view(ctx, instance):
    instance = instance.upper()
    if instance in config['instances']:
        block = config[instance]['blocks']
        lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        lister2 = [ '1 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25', '26 - 30', '31 - 35', '36 - 40', '41 - 45', '46 - 50' ]

        msg = ""
        for blk in range(0, int(block)):
            msg += "[{:>7}]: {}\n".format(lister2[blk], config[instance][lister[blk]])
        msg += "[{:>7}]: {}\n".format("TopOff", config[instance]['topoff'])

        panel = await ctx.send(f"```{msg}```")

        for blk in range(0, int(block)):
            await panel.add_reaction(config['Emoji'][lister[blk]])
        await panel.add_reaction(config['Emoji']['topoff'])
        await panel.add_reaction(config['Emoji']['stop'])
        
        def check(reaction, user):
            return str(user).startswith("Happy") == False and str(reaction.emoji)[2:-1] in config['Emoji'].values()
        
        
        try:
            while True:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
                #user = ctx.message.author
                key = ''
                for k,v in config['Emoji'].items():
                    if str(reaction.emoji)[2:-1] == v:
                        if v == config['Emoji']['stop']:
                            await ctx.send(f"Terminating. Use /view {instance} to re-enable me.")
                            await panel.clear_reactions()
                            return
                        else:
                            key = k

                if config[instance][key] == '':
                    config.set(instance, key, user.display_name)

                elif config[instance][key] != '':
                    if authorized(user.roles):
                        config.set(instance, key, '')
                        
                else:
                    print(config[instance][key])

                with open('donatorConfig.ini', 'w') as f:
                    config.write(f)
                await panel.edit(content=f"```{new_panel(block, lister2, instance, lister)}```")

            
                
        except asyncio.TimeoutError:
            await panel.clear_reactions()
            await ctx.send("Times up. Use /view <instance> to continue editing.")

@discord_client.command()
async def clear(ctx, instance):
    instance = instance.upper()
    if authorized(ctx.message.author.roles):
        if instance in config['instances']:
            block = config[instance]['blocks']
            lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
            for i in range(0, int(block)):
                config.set(instance, lister[i], '')
            config.set(instance, 'topoff', '')
            await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")

    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")


def new_panel(block, lister2, instance, lister):
    msg = ""
    for blk in range(0, int(block)):
        msg += "[{:>7}]: {}\n".format(lister2[blk], config[instance][lister[blk]])
    msg += "[{:>7}]: {}\n".format("TopOff", config[instance]['topoff'])
    return msg


@discord_client.command()
async def test(ctx):
    for i in ctx.guild.emojis:
        print(i.name)
        print(i.id)
    return


def authorized(users_roles):
    for role in users_roles:
        if role.name == "CoC Leadership":
            return True
    return False


if __name__ == "__main__":
    discord_client.run(config['Bot']['Bot_Token'])