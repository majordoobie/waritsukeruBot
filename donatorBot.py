from discord.ext import commands
import discord
from configparser import ConfigParser
import asyncio

config = ConfigParser(allow_no_value=True)
config.read('donatorConfig.ini')
#config.read('/root/bots/waritsukeruBot/donatorConfig.ini')
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
    desc = ("My name is Happy, the Exceed donation bot! Use me to create instances of volunteer requests. Create an instance "
    "by supplying a name and the amount of blocks you want to create. 1 block equals 5 bases.\n\nOnce you create your instance "
    "you can view the panel with a /view <instance> command. This will display the panel with the corresponding reactions that users can "
    "click on. When a user clicks on the reaction, their discord name will be displayed on the panel. Only CoC Leaders can unregister "
    "a clan mates call.")
    embed = discord.Embed(title='Happy!', description= desc, color=0x8A2BE2)

    create = ("Command to create a new instance of a donation panel. The command takes two arguments "
    "a name, and a quantity. The name can be anything for example, the clan that is currently using it. Quantity is "
    "the ammount of blocks you would like to display. To use spaces between names, please use quotes.\n "
    "Example:\n"
    '/create "CWL Zulu Day 3" 4\n'
    '/view "CWL Zulu Day 3"')
    embed.add_field(name="""/create <string> <int>""", value=create, inline=False)

    listt = ("Command to list already created instances.")
    embed.add_field(name="""/listing""", value=listt, inline=False)

    view = ("View an instance already create in active mode. A user simply clicks on the emoji to register for the block. "
    "By default the panel will expire in 60 seconds. You can supply and an optional timeout in seconds. Be aware of not activating "
    "multiple instances as it will result in unpredicted behavior. Use the <stop> emoji to quickly stop an active panel.")
    embed.add_field(name="""/view <instance> <timeout:seconds>""", value=view, inline=False)

    delete = ("Delete an instance.")
    embed.add_field(name="""/delete <instance>""", value=delete, inline=False)

    clear = ("Clear an instance.")
    embed.add_field(name="""/clear <instance>""", value=clear, inline=False)

    edit = "Edit an instances available blocks. You can either add or subtract while maintaining the topoff value."
    embed.add_field(name="""/edit <instance> <(+/-) int>""", value=edit, inline=False)

    example = ("----------------\nExamples")
    val = ("""/create "CWL Zulu Day 3" 4 \n/view "CWL Zulu Day 3"\n/clear "CWL Zulu Day 3\n/edit "CWL Zulu Day 3" +2 
    
    \n\n\nwaritsukeruBot Version 1.2\nhttps://github.com/majordoobie/waritsukeruBot""")
    embed.add_field(name=example, value=val, inline=False)
    await ctx.send(embed = embed)





@discord_client.command()
async def create(ctx, name, block):
    if authorized(ctx.message.author.roles):
        name = name.title()
        if block.isdigit():
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
    #await ctx.send(embed = discord.Embed(title="**Instances:**", color=0x8A2BE2))
    await ctx.send("__**Instances**__")
    for instance in config['instances']:
        await ctx.send(f"```{'':>6}{instance.title():<20} Blocks: {config[instance.title()]['blocks']}```")

@discord_client.command()
async def delete(ctx, instance):
    instance = instance.title()
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


def new_panel(block, instance):
    lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    lister2 = [ '1 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25', '26 - 30', '31 - 35', '36 - 40', '41 - 45', '46 - 50' ]
    lister3 = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]

    msg = ""
    for blk in range(0, int(block)):
        tf = 'TopOff'
        #msg += "[{:2>}][{:>7}]: {}\n".format(lister3[blk], lister2[blk], config[instance][lister[blk]])
        msg += f"[{lister3[blk]:>2}][{lister2[blk]:>7}]: {config[instance][lister[blk]]}\n"
    msg += f"[ ~][{tf:>7}]: {config[instance]['topoff']}"
    #msg += "[ ~][{:>7}]: {}\n".format("TopOff", config[instance]['topoff'])
    return msg


@discord_client.command()
async def view(ctx, instance, *opt):
    if opt:
        var = opt[0]
        if var.isdigit():
            timeout = var
    else:
        timeout = 60

    instance = instance.title()
    if instance in config['instances']:
        lister = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        block = config[instance]['blocks']
        msg = new_panel(block, instance)

        # for blk in range(0, int(block)):
        #     msg += "[{:>2}][{:>7}]: {}\n".format(lister3[blk], lister2[blk], config[instance][lister[blk]])
        # msg += "[ ~][{:>7}]: {}\n".format("TopOff", config[instance]['topoff'])

        await ctx.send(embed = discord.Embed(title=f"**Instance: {instance}**", color=0x8A2BE2))
        panel = await ctx.send(f"```{msg}```")

        for blk in range(0, int(block)):
            await panel.add_reaction(config['Emoji'][lister[blk]])
        await panel.add_reaction(config['Emoji']['topoff'])
        await panel.add_reaction(config['Emoji']['stop'])
        
        
        
        def check(reaction, user):
            #Change this when moving to real
            #return str(user).startswith("Happy") == False and str(reaction.emoji)[2:-1] in config['Emoji'].values()
            return str(user).startswith("Kitty") == False and str(reaction.emoji)[2:-1] in config['Emoji'].values()
        
        bishop = True
        try:
            while bishop:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout = int(timeout), check=check)
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
                    if authorized(user.roles):
                        config.set(instance, key, '')
                        
                else:
                    print(config[instance][key])

                with open('donatorConfig.ini', 'w') as f:
                    config.write(f)

                await panel.edit(content=f"```{new_panel(block,instance)}```")
        
        except asyncio.TimeoutError:
            await panel.clear_reactions()
            await ctx.send(f"Times up! Use /view {instance} to re-enable panel. <a:{config['Emoji']['nyancat_big']}>")
            bishop = False

@discord_client.command()
async def edit(ctx, instance, quant):
    if authorized(ctx.message.author.roles):
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
                    await ctx.send(embed = discord.Embed(title=f"Block Range Error:\n\nNew Block Size: [ {new_block} ] \n(1<= [ Block Size ] <=10)", color=0xFF0000))
                    return
            elif operation == "-":
                new_block = int(old_block) - int(value)
                if 1 <= int(new_block) <=10:
                    pass
                else:
                    await ctx.send(embed = discord.Embed(title=f"Block Range Error:\n\nNew Block Size: [ {new_block} ] \n(1<= [ Block Size ] <=10)", color=0xFF0000))
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
    instance = instance.title()
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