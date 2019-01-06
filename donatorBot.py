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
    desc = ("Waritsukeru, the donation bot. Create new isntances with however many blocks you would like to set up.")
    embed = discord.Embed(title='Waritsukeru!', description= desc, color=0x8A2BE2)

    create = ("Command to create a new instance of a donate volunteer panel. The command takes two arguments "
    "a name, and a quantity. The name can be anything for example, the clan that is currently using it. Quantity is "
    "the ammount of blocks you would like to display. 3 will display 1[1 - 5], 2[5 - 10], 3[11 - 15].\nNOTE: no spaces in name.")
    embed.add_field(name="""/create <string> <int>""", value=create, inline=False)

    listt = ("Command to list already created instances.")
    embed.add_field(name="""/listt *two t's""", value=listt, inline=False)

    view = ("View an instance already created.")
    embed.add_field(name="""/view <isntance>""", value=view, inline=False)

    delete = ("Delete an instance")
    embed.add_field(name="""/delete <isntance>""", value=delete, inline=False)

    example = ("Examples")
    val = ("""/create "cwl zulu" 3 \n/view "cwl zulu" """)
    embed.add_field(name=example, value=val, inline=False)
    await ctx.send(embed = embed)





@discord_client.command()
async def create(ctx, name, block):
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

@create.error
async def create_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))


@discord_client.command()
async def listt(ctx):
    await ctx.send(embed = discord.Embed(title="Instances", color=0x8A2BE2))
    for instance in config['instances']:
        await ctx.send(f"```{instance}```")

@discord_client.command()
async def delete(ctx, instance):
    if instance in config['instances']:
        config['instances'].pop(instance)
        config.pop(instance)
        with open('donatorConfig.ini', 'w') as f:
            config.write(f)
        
        await ctx.send(f"<:{config['Emoji']['happy']}> Aye!")
    else:
        await ctx.send(f"Did not find {instance}. Please make sure you have used quotes or match case. Copy+Past from /list_int")

@delete.error
async def delete_handler(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def view(ctx, instance):
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
        await panel.add_reaction(config['Emoji']['twist'])
        await panel.add_reaction(config['Emoji']['stop'])
        
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji)[2:-1] in config['Emoji'].values()
        
        
        try:
            while True:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
                key = ''
                for k,v in config['Emoji'].items():
                    if str(reaction.emoji)[2:-1] == v:
                        print(k)
                        if v == config['Emoji']['stop']:
                            await ctx.send(f"Terminating. User /view {instance} to re-enable me.")
                            await panel.clear_reactions()
                            return
                        else:
                            key = k

                if config[instance][key] == user.name:
                    config.set(instance, key, '')
                else:
                    config.set(instance, key, user.name)

                with open('donatorConfig.ini', 'w') as f:
                    config.write(f)
                await panel.edit(content=f"```{new_panel(block, lister2, instance, lister)}```")

            
                
        except asyncio.TimeoutError:
            await panel.clear_reactions()
            await ctx.send("Times up. Use /view <instance> to continue editing.")
        
def new_panel(block, lister2, instance, lister):
    msg = ""
    for blk in range(0, int(block)):
        msg += "[{:>7}]: {}\n".format(lister2[blk], config[instance][lister[blk]])
    msg += "[{:>7}]: {}\n".format("TopOff", config[instance]['topoff'])
    return msg


@discord_client.command()
async def test(ctx, *, arg2):
    pass

if __name__ == "__main__":
    discord_client.run(config['Bot']['Bot_Token'])