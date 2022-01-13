import glob
import os
import sys
from pathlib import Path

import hikari
import datetime
import lightbulb
import yaml
from lightbulb import *

from hensyuusiro import *

pretime_dict = {}
client = lightbulb.BotApp(token=R_TOKEN, prefix="!")




@client.listen()
async def voiceevent(event: hikari.VoiceStateUpdateEvent) -> None:
    try:
        if event.state.channel_id == T_VOICE_EDITING_CHANNEL_ID or event.old_state.channel_id == T_VOICE_EDITING_CHANNEL_ID:
            user_id = str(event.state.user_id)
            file = "../hensyuusiro/user/" + user_id + ".yml"
            data = dict(
                Username=str(event.state.member.username),
                Total_Editing_Time=0,
                Total_Video_Time=0,
                Start_Video_Time="00:00:00",
                End_Video_Time="00:00:00"

            )
            fa = glob.glob(file)
            fa = "".join(fa)

            if file == fa:
                print("アカウントデータが存在するのでファイルを読み込みます")
                with open(file, "r") as yml:
                    config = yaml.safe_load(yml)
                    print(config)
            else:
                print("アカウントデータがないので作成します")
                with open(file, "wt") as outfile:
                    outfile.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))
            # print("ボイスチャンネルで変化がありました!!")

            if event.old_state is None:

                pretime_dict[event.state.user_id] = datetime.datetime.now()
                print("記録しています！！")
            else:
                print("記録を終わりました。")
                duration_time = pretime_dict[event.old_state.user_id] - datetime.datetime.now()
                duration_time_adjust = int(duration_time.total_seconds()) * -1
                total_editing_time = config["Total_Editing_Time"] + duration_time_adjust
                data = dict(
                    Username=str(event.state.member.username),
                    Total_Editing_Time=total_editing_time,
                    Total_Video_Time=config["Total_Video_Time"],
                    Start_Video_Time="00:00:00",
                    End_Video_Time="00:00:00"

                )
                with open(file, "w") as filer:
                    filer.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))
                embed = hikari.Embed(color="00fa9a")
                user = event.old_state.member.user.username
                embed.set_author(name=user + "の編集記録", icon=event.old_state.member.user.avatar_url)
                editing_time_hours = duration_time_adjust // 3600
                editing_time_minutes = (duration_time_adjust - editing_time_hours * 3600) //60
                editing_time_seconds = (duration_time_adjust - editing_time_hours * 3600) %60
                total_editing_time_hours = total_editing_time // 3600
                total_editing_time_minutes = (total_editing_time - total_editing_time_hours * 3600) // 60
                total_editing_time_seconds = (total_editing_time - total_editing_time_hours * 3600) % 60

                embed.add_field(name="編集時間", value=str(editing_time_hours) + "時" + str(editing_time_minutes) + "分" + str(editing_time_seconds) + "秒")
                embed.add_field(name="累計編集時間",
                                value=str(total_editing_time_hours) + "時" + str(total_editing_time_minutes) + "分" + str(total_editing_time_seconds) + "秒")

                await (await client.rest.fetch_channel(T_EDITING_CHANNEL_ID)).send(embed=embed)
    except AttributeError:
        pass


@client.command()
@lightbulb.decorators.option("start", "text to repeat", modifier=commands.OptionModifier.CONSUME_REST)
@lightbulb.command("start", "動画時間を記録します。", aliases="s")
@lightbulb.implements(lightbulb.PrefixCommand)
async def video_time_start(ctx: lightbulb.Context) -> None:
    try:
        if ctx.get_guild().get_voice_state(ctx.user).channel_id == T_VOICE_EDITING_CHANNEL_ID:

            print(ctx.options.start)
            print(type(ctx.options.start))
            old_hours = ctx.options.start[0:2]
            old_minutes = ctx.options.start[3:5]
            old_seconds = ctx.options.start[6:8]
            if type(old_hours) and type(old_minutes) and type(old_minutes) != str:
                pass
            else:
                try:
                    int(old_hours)
                    int(old_minutes)
                    int(old_seconds)
                    print(str(old_hours + old_minutes + old_seconds))
                    # await ctx.respond("どうがじかんを記録します。\n"+"動画時間：" +
                    # str(old_hours) + "時" +
                    # str(old_minutes) + "分" +
                    # str(old_seconds) + "秒")
                    embed = hikari.Embed(color="00fa9a")
                    user = ctx.user.username
                    embed.set_author(name=user + "の動画記録", icon=ctx.member.user.avatar_url)
                    embed.add_field(name="動画時間を記録します。", value="開始動画時間：" +
                                                              str(old_hours) + "時" +
                                                              str(old_minutes) + "分" +
                                                              str(old_seconds) + "秒")
                    file = "../hensyuusiro/user/" + str(ctx.member.user.id) + ".yml"
                    with open(file, "r") as yml:
                        config = yaml.safe_load(yml)
                        data = dict(
                            Username=config["Username"],
                            Total_Editing_Time=config["Total_Editing_Time"],
                            Total_Video_Time=config["Total_Video_Time"],
                            Start_Video_Time=ctx.options.start,
                            End_Video_Time=config["End_Video_Time"]

                        )
                        with open(file, "w") as filer:
                            filer.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))

                    await (await client.rest.fetch_channel(T_EDITING_CHANNEL_ID)).send(embed=embed)
                except ValueError:
                    await ctx.respond("おっぱいがいっぱい")
    except AttributeError:
        embed = hikari.Embed(color="b22222")
        embed.add_field(name="実行されませんでした。", value="ボイスチャンネルに接続してから実行してください。")
        await (await client.rest.fetch_channel(T_EDITING_CHANNEL_ID)).send(embed=embed)


@client.command()
@lightbulb.decorators.option("end", "text to repeat", modifier=commands.OptionModifier.CONSUME_REST)
@lightbulb.command("end", "動画時間を記録します。", aliases="e")
@lightbulb.implements(lightbulb.PrefixCommand)
async def video_time_end(ctx: lightbulb.Context) -> None:
    try:
        if ctx.get_guild().get_voice_state(ctx.user).channel_id == T_VOICE_EDITING_CHANNEL_ID:
            print(ctx.get_guild().get_voice_state(ctx.user))
            print(ctx.options.end)
            print(type(ctx.options.end))
            new_hours = ctx.options.end[0:2]
            new_minutes = ctx.options.end[3:5]
            new_seconds = ctx.options.end[6:8]
            if type(new_hours) and type(new_minutes) and type(new_seconds) != str:
                pass
            else:
                try:
                    hours = int(new_hours) * 3600
                    minutes = int(new_minutes) * 60
                    seconds = int(new_seconds)
                    total_new_video_time = hours + minutes + seconds
                    embed = hikari.Embed(color="00fa9a")
                    user = ctx.user.username
                    embed.set_author(name=user + "の動画記録", icon=ctx.member.user.avatar_url)
                    embed.add_field(name="動画時間を記録し終わりました。", value="終了動画時間：" +
                                                                  str(new_hours) + "時" +
                                                                  str(new_minutes) + "分" +
                                                                  str(new_seconds) + "秒")
                    file = "../hensyuusiro/user/" + str(ctx.member.user.id) + ".yml"
                    with open(file, "r") as yml:
                        config = yaml.safe_load(yml)
                        total_old_video_time = int(config["Start_Video_Time"][0:2]) * 3600 + int(
                            config["Start_Video_Time"][3:5]) * 60 + int(config["Start_Video_Time"][6:8])
                        # var_hours = hours - int(config["Start_Video_Time"][0:2])
                        # var_minutes = minutes - int(config["Start_Video_Time"][3:5])
                        # var_seconds = seconds- int(config["Start_Video_Time"][6:8])
                        dif_total_video_time = total_new_video_time - total_old_video_time
                        dif_hours = dif_total_video_time // 3600
                        dif_minutes = (dif_total_video_time - dif_hours * 3600) // 60
                        dif_seconds = (dif_total_video_time - dif_hours * 3600) % 60
                        total_video_time = dif_total_video_time + config["Total_Video_Time"]
                    with open(file, "r") as ymla:
                        config = yaml.safe_load(ymla)
                        data = dict(
                            Username=config["Username"],
                            Total_Editing_Time=config["Total_Editing_Time"],
                            Total_Video_Time=total_video_time,
                            Start_Video_Time=config["Start_Video_Time"],
                            End_Video_Time=str(ctx.options.end)

                        )
                        with open(file, "w") as filer:
                            filer.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))
                        embed.add_field(name="動画編集時間",
                                        value=str(dif_hours) + "時" + str(dif_minutes) + "分" + str(dif_seconds) + "秒")
                        await (await client.rest.fetch_channel(T_EDITING_CHANNEL_ID)).send(embed=embed)
                except ValueError:
                    await ctx.respond("おっぱいがいっぱい")
    except AttributeError:
        print(ctx.get_guild().get_voice_state(ctx.user))
        print(ctx.options.end)
        print(type(ctx.options.end))
        new_hours = ctx.options.end[0:2]
        new_minutes = ctx.options.end[3:5]
        new_seconds = ctx.options.end[6:8]
        if type(new_hours) and type(new_minutes) and type(new_seconds) != str:
            pass
        else:
            try:
                hours = int(new_hours) * 3600
                minutes = int(new_minutes) * 60
                seconds = int(new_seconds)
                total_new_video_time = hours + minutes + seconds
                embed = hikari.Embed(color="00fa9a")
                user = ctx.user.username
                embed.set_author(name=user + "の動画記録", icon=ctx.member.user.avatar_url)
                embed.add_field(name="動画時間を記録し終わりました。", value="終了動画時間：" +
                                                              str(new_hours) + "時" +
                                                              str(new_minutes) + "分" +
                                                              str(new_seconds) + "秒")
                file = "../hensyuusiro/user/" + str(ctx.member.user.id) + ".yml"
                with open(file, "r") as yml:
                    config = yaml.safe_load(yml)
                    total_old_video_time = int(config["Start_Video_Time"][0:2]) * 3600 + int(
                        config["Start_Video_Time"][3:5]) * 60 + int(config["Start_Video_Time"][6:8])
                    # var_hours = hours - int(config["Start_Video_Time"][0:2])
                    # var_minutes = minutes - int(config["Start_Video_Time"][3:5])
                    # var_seconds = seconds- int(config["Start_Video_Time"][6:8])
                    dif_total_video_time = total_new_video_time - total_old_video_time
                    dif_hours = dif_total_video_time // 3600
                    dif_minutes = (dif_total_video_time - dif_hours * 3600) // 60
                    dif_seconds = (dif_total_video_time - dif_hours * 3600) % 60
                    total_video_time = dif_total_video_time + config["Total_Video_Time"]
                with open(file, "r") as ymla:
                    config = yaml.safe_load(ymla)
                    data = dict(
                        Username=config["Username"],
                        Total_Editing_Time=config["Total_Editing_Time"],
                        Total_Video_Time=total_video_time,
                        Start_Video_Time=config["Start_Video_Time"],
                        End_Video_Time=str(ctx.options.end)

                    )
                    with open(file, "w") as filer:
                        filer.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))
                    embed.add_field(name="動画編集時間",
                                    value=str(dif_hours) + "時" + str(dif_minutes) + "分" + str(dif_seconds) + "秒")
                    await (await client.rest.fetch_channel(T_EDITING_CHANNEL_ID)).send(embed=embed)
            except ValueError:
                await ctx.respond("おっぱいがいっぱい")


@client.command()
@lightbulb.command("stats", "今までの記録を確認できます。")
@lightbulb.implements(lightbulb.PrefixCommand)
async def stats(ctx: lightbulb.Context) -> None:
    file = "../hensyuusiro/user/" + str(ctx.member.user.id) + ".yml"
    with open(file, "r") as yml:
        config = yaml.safe_load(yml)
        Total_Editing_Time_Hours = config["Total_Editing_Time"] // 3600
        Total_Editing_Time_Minutes = (config["Total_Editing_Time"] - Total_Editing_Time_Hours * 3600) // 60
        Total_Editing_Time_Seconds = (config["Total_Editing_Time"] - Total_Editing_Time_Hours * 3600) // 60
        Total_Video_Time_Hours = config["Total_Video_Time"] // 3600
        Total_Video_Time_Minutes = (config["Total_Video_Time"] - Total_Video_Time_Hours * 3600) // 60
        Total_Video_Time_Seconds = (config["Total_Video_Time"] - Total_Video_Time_Hours * 3600) // 60
        embed = hikari.Embed(color="afeeee")
        embed.set_author(name=ctx.member.username + "の記録", icon=ctx.member.user.avatar_url)
        embed.add_field(name="累計編集時間",
                        value=str(Total_Editing_Time_Hours) + "時" + str(Total_Editing_Time_Minutes) + "分" + str(
                            Total_Editing_Time_Seconds) + "秒")
        embed.add_field(name="累計動画編集時間",
                        value=str(Total_Video_Time_Hours) + "時" + str(Total_Video_Time_Minutes) + "分" + str(
                            Total_Video_Time_Seconds) + "秒")
        await(await client.rest.fetch_channel(T_EDITING_CHANNEL_ID)).send(embed=embed)

client.run()
