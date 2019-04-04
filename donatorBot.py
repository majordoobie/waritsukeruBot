from APIs.discordBotAPI import BotAssist
from requests import get
from discord.ext import commands
import discord
from configparser import ConfigParser
import asyncio
from sys import argv
from sys import exit as ex # Avoid exit built in
import os

#####################################################################################################################
                                             # Set up the environment
#####################################################################################################################
# Look for either the dev or live switch
if len(argv) == 2:
    if argv[-1] == "--live":
        botMode = "liveBot"
    elif argv[-1] == "--dev":
        botMode = "devBot"
    else:
        ex("\n[ERROR] Make sure to add the right switch to activate me.")
else:
    ex("\n[ERROR] Make sure to add the right switch to activate me.")

# Create config object 
config = ConfigParser(allow_no_value=True)

# Read the configuratino file based on mode
if botMode == "liveBot":
    configLoc = ''
    if os.path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}".split(' '))
    discord_client.remove_command("help")

elif botMode == "devBot":
    configLoc = 'Configuration/happyConfig.ini'
    if os.path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}".split(' '))
    discord_client.remove_command("help")

else:
    ex("Switch not found")

# Instanciate botAPI
botAPI = BotAssist(botMode, configLoc)
prefx = config[botMode]['bot_Prefix'].split(' ')[0]
#####################################################################################################################
                                             # Discord Commands [info]
#####################################################################################################################
@discord_client.event
async def on_ready():
    """
    Simple funciton to display logged in data to terminal
    """
    print(f'\n\nLogged in as: {discord_client.user.name} - {discord_client.user.id}\nDiscord Version: {discord.__version__}\n'
        f"\nRunning in [{botMode}] mode\n"
        "------------------------------------------\n"
        f"Prefix set to:          {prefx}\n"
        f"Config file set to:     {configLoc}\n"
        f"Current exit node:      {get('https://api.ipify.org').text}\n"
        "------------------------------------------")

    game = discord.Game(config[botMode]['game_msg'])
    await discord_client.change_presence(status=discord.Status.online, activity=game)

@discord_client.command()
async def help(ctx):
    """ Command to display the help menu """

    desc = ("My name is Happy, the Exceed donation bot! Use me to create instances of volunteer requests. Create an instance "
    "by supplying a name and the amount of blocks you want to create. 1 block equals 5 bases.\n\nOnce you create your instance "
    "you can view the instance panel with a /view <instance> command. This will display the panel with the corresponding reactions that users can "
    "click on. When a user clicks on the reaction, their discord name will be displayed on the panel. Only CoC Leaders can unregister "
    "a clan mates call.\n\n")
    embed = discord.Embed(title='Happy!', description= desc, color=0x8A2BE2)

    create = ("Command to create a new instance panel. The command takes two arguments: "
    "a name, and a quantity. The name can be anything for example, the clan that is currently using it. Quantity is "
    "the ammount of blocks you would like to display. To use spaces between names, please use quotes.\n "
    "Example:\n"
    '/create "CWL Zulu Day 3" 4\n'
    '/view "CWL Zulu Day 3 --timeout 20m"\n\n')
    embed.add_field(name="""/create <string> <int>""", value=create, inline=False)

    listt = ("Command to list already created instances.")
    embed.add_field(name="""/listing""", value=listt, inline=False)

    view = ("View an instance already create in active mode. A user simply clicks on the emoji to register for the block. "
    "By default the panel will expire in 60 seconds. You can supply and an optional timeout option. Be aware of not activating "
    "multiple instances as it will result in unpredicted behavior. Use the <stop> emoji to quickly stop an active panel.\n\n"
    "Switches supported:\n"
    "--timeout 20s ::--> Stops panel in 20 seconds\n"
    "--timeout 20m ::-> Stops panel in 20 minutes\n"
    "--timeout 20h ::--> Stops panel in 20 hours\n"
    "--persistent ::-----> Prevent panel from expiring\n [USE STOP BEFORE OPENING NEW PANEL]"
    "")
    embed.add_field(name="""/view <instance> <swtich>""", value=view, inline=False)

    delete = ("Delete an instance.\n\n")
    embed.add_field(name="""/delete <instance>""", value=delete, inline=False)

    clear = ("Clear an instance.\n\n")
    embed.add_field(name="""/clear <instance>""", value=clear, inline=False)

    edit = "Edit an instances available blocks. You can either add or subtract while maintaining the topoff value.\n\n"
    embed.add_field(name="""/edit <instance> <(+/-) int>""", value=edit, inline=False)

    dbug = "/killbot\n/mode"
    embed.add_field(name="""Debugging""", value=dbug, inline=False)

    example = ("-----------------------\nExamples")
    val = ("""/create "CWL Zulu Day 3" 4 \n/view "CWL Zulu Day 3"\n/clear "CWL Zulu Day 3\n/edit "CWL Zulu Day 3" +2 
    
    \n\n\nwaritsukeruBot Version 1.3\nhttps://github.com/majordoobie/waritsukeruBot""")
    embed.add_field(name=example, value=val, inline=False)
    await ctx.send(embed = embed)

@discord_client.command()
async def killbot(ctx):
    if botAPI.rightServer(ctx, config) and botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("Wrong server or you're not authorized to use this.")

    await ctx.send("Tearing down, please hold.")
    # Find a way to close panel thread
    with open(configLoc, 'w') as f:
            config.write(f)
    await ctx.send("Logging out.")
    await discord_client.logout()
    return

@discord_client.command()
async def create(ctx, name, block):
    """ Command to create panel instance """
    if botAPI.rightServer(ctx, config) and botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("Wrong server or you're not authorized to use this.")

    name = name.title()
    if block.isdigit():
        if 1 <= int(block) <=10:
            pass
        else:
            await ctx.send(embed = discord.Embed(title=f"Index Range Error",description = f"Block Size: [ {block} ] \n(1<= [ Block Size ] <=10)", color=0xFF0000))
            return
        lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        config.set('instances', name, "False")
        config.add_section(name)
        config.set(name, "instance_name", name)
        config.set(name, "blocks", block)
        
        for blk in range(0, int(block)):
            config.set(name, lister[blk], '')
        config.set(name, "topoff", '')

        with open(configLoc, 'w') as f:
            config.write(f)

        await ctx.send(f"All set! Use {prefx}view {name} to activate your panel.")

    else:
        dsc = "Blocks argument must be an integer."
        await ctx.send(embed = discord.Embed(title="ARGUMENT ERROR", description=dsc, color=0xFF0000))
        return


@create.error
async def create_handler(ctx, error):
    """ Error handling for /create"""
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))


@discord_client.command()
async def listing(ctx):
    """ Command to list the panels already created """
    if botAPI.rightServer(ctx, config) and botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("Wrong server or you're not authorized to use this.")

    await ctx.send("__**Instances**__")
    for instance in config['instances']:
        await ctx.send(f"```{'':>6}{instance.title():<20} Blocks: {config[instance.title()]['blocks']}```")


@discord_client.command()
async def delete(ctx, instance):
    """ Command to remove panel instances from listing """
    if botAPI.rightServer(ctx, config) and botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("Wrong server or you're not authorized to use this.")

    instance = instance.title()
    if instance in config['instances']:
        config['instances'].pop(instance)
        config.pop(instance)
        with open(configLoc, 'w') as f:
            config.write(f)
        
        await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")
    else:
        await ctx.send(f"Did not find {instance}. Please make sure you have used quotes or match case. Copy+Past from /list_int")

@delete.error
async def delete_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))


@discord_client.command()
async def view(ctx, instance, *opt):
    """ Command is used to display the actual panel """
    if botAPI.rightServer(ctx, config) and botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("Wrong server or you're not authorized to use this.")

    # Set timeout 
    if opt:
        if len(opt) == 1:
            if opt[0] in ["--persistent", "-p"]:
                timeout = None
            else:
                await ctx.send(embed = discord.Embed(title="ARG ERROR\nInvalid options used. Try /help", color=0xFF0000))
                return
        elif len(opt) == 2:
            if opt[0] in ["--timeout", "-t"]:
                num, form = opt[1][:-1], opt[1][-1]
                if num.isdigit():
                    if form.lower() in ['s','m','h']:
                        if form.lower() == 's':
                            timeout = int(num)
                        elif form.lower() == 'm':
                            timeout = int(num) * 60
                        elif form.lower() == 'h':
                            timeout = int(num) * 60 * 60
                    else:
                        await ctx.send(embed = discord.Embed(title="ARG ERROR\nInvalid options used. Try /help", color=0xFF0000))
                        return 
                else:
                    await ctx.send(embed = discord.Embed(title="ARG ERROR\nInvalid options used. Try /help", color=0xFF0000))
                    return
            else:
                await ctx.send(embed = discord.Embed(title="ARG ERROR\nInvalid options used. User /Try", color=0xFF0000))
                return
        else:
            await ctx.send(embed = discord.Embed(title="ARG ERROR\nInvalid options used. Try /help", color=0xFF0000))
            return
    else:
        timeout = 60

    # Open the panel
    instance = instance.title()
    # Check if the instance name is in the file
    print(config['instances'][instance])
    if instance in config['instances']:
        pass
    else:
        await ctx.send(embed = discord.Embed(title=f"INSTANCE ERROR\nInstance [{instance}] was not found.", color=0xFF0000))
        return
        
    # Check to make sure that the panel isn't already open
    if config["instances"][instance] == "False":
        config["instances"][instance] = "True"
        with open(configLoc, 'w') as f:
                config.write(f)
    else:
        await ctx.send(embed = discord.Embed(title=f"INSTANCE ERROR\nInstance [{instance}] Is already open.", color=0xFF0000))
        return


    # Start to create the panels
    lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    block = config[instance]['blocks']

    # Grab a new panel 
    msg = new_panel(block, instance)

    header = (f"**Instance:** {instance}\n**Timeout:** {timeout} seconds")
    await ctx.send(header)
    panel = await ctx.send(f"```{msg}```")

    # Add the emojis
    for blk in range(0, int(block)):
        await panel.add_reaction(config['Emoji'][lister[blk]])
    await panel.add_reaction(config['Emoji']['topoff'])
    await panel.add_reaction(config['Emoji']['stop'])
    
    
    
    def check(reaction, user):
        # Make sure that the reaction is for the correct message 
        if panel.id == reaction.message.id:
            # check that the reaction is within our list of reactions and not the bot
            return user.bot == False and str(reaction.emoji)[2:-1] in config['Emoji'].values()
        else:
            return False
         
    bishop = True
    try:
        while bishop:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout = timeout, check=check)
            key = ''
            for k,v in config['Emoji'].items():
                if str(reaction.emoji)[2:-1] == v:
                    if v == config['Emoji']['stop']:
                        await ctx.send(f"Terminating. Use /view {instance} to re-enable panel.")
                        await panel.clear_reactions()
                        config["instances"][instance] = "False"
                        with open(configLoc, 'w') as f:
                                config.write(f)
                        bishop = False
                        return
                    else:
                        key = k

            if config[instance][key] == '':
                config.set(instance, key, user.display_name)

            elif config[instance][key] != '':
                if authorized(user):
                    config.set(instance, key, '')
                    
            else:
                print(config[instance][key])

            with open(configLoc, 'w') as f:
                config.write(f)

            await panel.edit(content=f"```{new_panel(block,instance)}```")
    
    except asyncio.TimeoutError:
        await panel.clear_reactions()
        config["instances"][instance] = "False"
        with open(configLoc, 'w') as f:
                config.write(f)
        await ctx.send(f"Times up! Use /view {instance} to re-enable panel. <a:{config['Emoji']['nyancat_big']}>")
        bishop = False
    

@view.error
async def view_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def edit(ctx, instance, quant):
    if botAPI.rightServer(ctx, config) and botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("Wrong server or you're not authorized to use this.")

    instance = instance.title()
    if quant[0] in ['+', '-']:
        if quant[1:].isdigit():
            operation = quant[0]
            value = quant[1:]
        else:
            await ctx.send(embed = discord.Embed(title="INPUT ERROR\nValue must be a integer", color=0xFF0000))
            return
    else:
        await ctx.send(embed = discord.Embed(title="INPUT ERROR\nOperator must be + or -.", color=0xFF0000))
        return


    if instance in config['instances']:
        old_block = config[instance]['blocks']
        if operation == "+":
            new_block = int(old_block) + int(value)
            if 1 <= int(new_block) <=10:
                pass
            else:
                await ctx.send(embed = discord.Embed(title=f"Index Range Error",description = f"Block Size: [ {new_block} ] \n(1<= [ Block Size ] <=10)", color=0xFF0000))
                return
        elif operation == "-":
            new_block = int(old_block) - int(value)
            if 1 <= int(new_block) <=10:
                pass
            else:
                await ctx.send(embed = discord.Embed(title=f"Index Range Error",description = f"Block Size: [ {new_block} ] \n(1<= [ Block Size ] <=10)", color=0xFF0000))
                return

        config.set(instance, "blocks", str(new_block)) # set new blocks value
        topoffVal = config[instance]['topoff']
        config[instance].pop('topoff')
        lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

        if int(old_block) < int(new_block):
            for i in range(0, int(new_block)):
                if lister[i] in config[instance]:
                    pass
                else:
                    config.set(instance, lister[i], '')
            config.set(instance, "topoff", topoffVal)
            await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")
            return

        elif int(old_block) > int(new_block):
            for i in range(int(new_block), int(old_block)):
                config[instance].pop(lister[i])
            config.set(instance, "topoff", topoffVal)
            await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")
            return
    else:
        await ctx.send(embed = discord.Embed(title="INPUT ERROR\nNo instance of that name available.", color=0xFF0000))
        return


@edit.error
async def edit_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def clear(ctx, instance):
    """ Command to clear out a panel """
    if botAPI.rightServer(ctx, config) and botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("Wrong server or you're not authorized to use this.")

    instance = instance.title()
    if instance in config['instances']:
        block = config[instance]['blocks']
        lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        for i in range(0, int(block)):
            config.set(instance, lister[i], '')
        config.set(instance, 'topoff', '')
        await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")
        return

@clear.error
async def clear_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))


@discord_client.command()
async def test(ctx):
    """ Only used for testing """
    print(ctx.author.bot)

###
 # Functions
###  
def new_panel(block, instance):
    """ Function to create panels """
    lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    lister2 = [ '1 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25', '26 - 30', '31 - 35', '36 - 40', '41 - 45', '46 - 50' ]
    lister3 = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]

    msg = ""
    for blk in range(0, int(block)):
        tf = 'TopOff'
        msg += f"[{lister3[blk]:>2}][{lister2[blk]:>7}]: {config[instance][lister[blk]]}\n"
    msg += f"[ ~][{tf:>7}]: {config[instance]['topoff']}"
    return msg

def authorized(user):
    if 294283611870461953 in ( role.id for role in user.roles ):
        return True
    else:
        return False
        
if __name__ == "__main__":
    discord_client.run(config[botMode]['bot_token'])
    