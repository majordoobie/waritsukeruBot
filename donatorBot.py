from discord.ext import commands
import discord
from configparser import ConfigParser
import asyncio
from sys import argv
from sys import exit as ex # Avoid exit built in
import os

#########
    # Set up the environment 
########
# Look for either the dev or live switch
if len(argv) == 2:
    if argv[-1] == "--live":
        botMode = "Live"
    elif argv[-1] == "--dev":
        botMode = "Dev"
    else:
        ex("\n[ERROR] Make sure to add the right switch to activate me.")
else:
    ex("\n[ERROR] Make sure to add the right switch to activate me.")

# Read the configuratino file based on mode
config = ConfigParser(allow_no_value=True)
if botMode == "Live":
    configLoc = '/root/bots/waritsukeruBot/donatorConfig.ini'
    if os.path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    discord_client = commands.Bot(command_prefix = f"{config['Bot']['bot_prefix']}")
    discord_client.remove_command("help")

elif botMode == "Dev":
    configLoc = 'donatorConfig.ini'
    if os.path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    discord_client = commands.Bot(command_prefix = "dev.")
    discord_client.remove_command("help")


####
    # Begining of bot commands
####
@discord_client.event
async def on_ready():
    print(f'\n\nLogged in as: {discord_client.user.name} - {discord_client.user.id}\nVDiscord Version: {discord.__version__}\n')
    print(f"Running in {botMode} mode.")
    if botMode == "Live":
        print(f"This mode uses: {config['Bot']['bot_Prefix']} as a prefix")
    if botMode == "Dev":
        print(f"This mode uses: [ dev. ] as a prefix")
    print(f"Config file set to: /{configLoc}")
    await discord_client.change_presence(status=discord.Status.online, activity=discord.Game("with Natzu"))

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
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return

    if authorized(ctx.message.author):
        await ctx.send("Tearing down, please hold.")
        # Find a way to close panel thread
        with open(configLoc, 'w') as f:
                config.write(f)
        await ctx.send("Logging out.")
        await discord_client.logout()
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

@discord_client.command()
async def create(ctx, name, block):
    """ Command to create panel instance """
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return

    if authorized(ctx.message.author):
        name = name.title()
        if block.isdigit():
            if 1 <= int(block) <=10:
                pass
            else:
                await ctx.send(embed = discord.Embed(title=f"Index Range Error",description = f"Block Size: [ {block} ] \n(1<= [ Block Size ] <=10)", color=0xFF0000))
                return
            lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
            config.set('instances', name)
            config.add_section(name)
            config.set(name, "instance_name", name)
            config.set(name, "blocks", block)
            
            for blk in range(0, int(block)):
                config.set(name, lister[blk], '')
            config.set(name, "topoff", '')

            with open(configLoc, 'w') as f:
                config.write(f)

            await ctx.send(f"All set! Use /view {name} to activate your panel.")

        else:
            dsc = "Blocks argument must be an integer."
            await ctx.send(embed = discord.Embed(title="ARGUMENT ERROR", description=dsc, color=0xFF0000))
            return
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

@create.error
async def create_handler(ctx, error):
    """ Error handling for /create"""
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))


@discord_client.command()
async def listing(ctx):
    """ Command to list the panels already created """
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return

    await ctx.send("__**Instances**__")
    for instance in config['instances']:
        await ctx.send(f"```{'':>6}{instance.title():<20} Blocks: {config[instance.title()]['blocks']}```")

@discord_client.command()
async def delete(ctx, instance):
    """ Command to remove panel instances from listing """
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return
    instance = instance.title()
    if authorized(ctx.message.author):
        if instance in config['instances']:
            config['instances'].pop(instance)
            config.pop(instance)
            with open(configLoc, 'w') as f:
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
async def view(ctx, instance, *opt):
    """ Command is used to display the actual panel """
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return
    # Set timeout 
    if opt:
        if len(opt) == 1:
            if opt[0] == "--persistent":
                timeout = None
            else:
                await ctx.send(embed = discord.Embed(title="ARG ERROR\nInvalid options used. Try /help", color=0xFF0000))
                return
        elif len(opt) == 2:
            if opt[0] == "--timeout":
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

    instance = instance.title()
    if instance in config['instances']:
        lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        block = config[instance]['blocks']
        msg = new_panel(block, instance)

        await ctx.send(f"**Instance:** {instance}")
        await ctx.send(f"**Timeout:** {timeout} seconds")
        panel = await ctx.send(f"```{msg}```")

        for blk in range(0, int(block)):
            await panel.add_reaction(config['Emoji'][lister[blk]])
        await panel.add_reaction(config['Emoji']['topoff'])
        await panel.add_reaction(config['Emoji']['stop'])
        
        
        
        def check(reaction, user):
            #Change this when moving to real
            if botMode == 'Dev':
                return str(user).startswith("Kitty") == False and str(reaction.emoji)[2:-1] in config['Emoji'].values()
            elif botMode == 'Live':
                return str(user).startswith("Happy") == False and str(reaction.emoji)[2:-1] in config['Emoji'].values()
            
        
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
            await ctx.send(f"Times up! Use /view {instance} to re-enable panel. <a:{config['Emoji']['nyancat_big']}>")
            bishop = False
    else:
        await ctx.send(embed = discord.Embed(title=f"INSTANCE ERROR\nInstance {instance} was not found.", color=0xFF0000))
        return

@view.error
async def view_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def edit(ctx, instance, quant):
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return

    if authorized(ctx.message.author):
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
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return
    instance = instance.title()
    if authorized(ctx.message.author):
        if instance in config['instances']:
            block = config[instance]['blocks']
            lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
            for i in range(0, int(block)):
                config.set(instance, lister[i], '')
            config.set(instance, 'topoff', '')
            await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")
            return

    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

@clear.error
async def clear_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def mode(ctx):
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return
    await ctx.send(f"```{wrongServer(ctx)}```")


@discord_client.command()
async def test(ctx):
    """ Only used for testing """
    if rightServer(ctx.guild):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{wrongServer(ctx)}```")
        return

###
 # Functions
###
def wrongServer(ctx):
    if botMode == "Live":
        servv = "Reddit Zulu"
    elif botMode == "Dev":
        servv = "DevTester"
    data = (
    f"BotName:      {discord_client.user.display_name}\n"
    f"Cur_Guild:    {ctx.guild.name}\n"
    f"Cur_GuildID:  {ctx.guild.id}\n"
    f"Set_Guild:    {servv}\n"
    f"Mode:         {botMode}\n"
    f"ConfigLoc:    {configLoc}\n"
    f"Pref:         {ctx.prefix}\n"
    f"Created:      {discord_client.user.created_at}"
    )
    return data

def authorized(user):
    """ Functionto make sure that the user is authorized to runt he command """
    if str(user.id) == str(config['Discord Roles']['server_keeper']):
        return True

    for role in user.roles:
        if role.name == "CoC Leadership":
            return True
    return False

def rightServer(guildObj):
    """ Function to make sure the bot is running on the proper channel based on botMode """
    if botMode == 'Live':
        if str(guildObj.id) == str(config['Discord']['zuludisc_id']):
            return True
        else:
            return False

    elif botMode == 'Dev':
        if str(guildObj.id) == str(config['Discord']['devTester_id']): 
            return True
        else:
            return False
  
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

if __name__ == "__main__":
    discord_client.run(config['Bot']['bot_Token'])
    