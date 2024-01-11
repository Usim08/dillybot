import discord
import os
from discord.interactions import Interaction
import pymongo
from discord.ext import commands
from discord import DMChannel
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.all()

bot = commands.Bot(command_prefix="!", intents=intents, application_id="1179791922815057930")


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Create a new client and connect to the server
client = pymongo.MongoClient("mongodb+srv://Usim:1234@cluster0.2mpijnh.mongodb.net/?retryWrites=true&w=majority")
db = client.PayNumber
print(db)


@bot.event
async def on_ready():
    channel = bot.get_channel(1179793861028102215)
    await bot.tree.sync()
    await channel.send("봇이 준비되었습니다!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Dilly 딜리"))
    print("봇 준비완료")


@bot.tree.command(name="어드민투딜리", description="해당 슬래시는 딜리매니저만 이용할 수 있어요")
async def password(interaction: discord.Interaction):
    if str(interaction.user.id) == str(751835293924982957):
        viewww = SelectAdmin()
        await interaction.response.send_message("선택사항을 선택하세요", view=viewww, ephemeral=True)
    else:
        embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description=f"{interaction.user.mention}님은 공지를 작성할 권한이 없어요")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SelectAdmin(View):
    @discord.ui.select(
        placeholder="선택사항 선택",
        options=[
            discord.SelectOption(
                label="딜리 인증",
                value='1',
                description="딜리의 서비스 시작을 위해 사용자를 인증합니다",
                emoji="✅"
            ),
            discord.SelectOption(
                label="공지하기",
                value='2',
                description="사용자들에게 다이렉트 메세지로 공지를 전송합니다",
                emoji="📣"
            ),
            discord.SelectOption(
                label="계좌확인",
                value='3',
                description="사용자의 계좌를 조회합니다",
                emoji="🔍"
            )
        ]
    )

    async def select_callback(self, interaction, select):
        select.disabled = True
        
        if select.values[0] == '1':
            await interaction.response.send_modal(Verify())
        if select.values[0] == '2':
            await interaction.response.send_modal(SendNofi())
        if select.values[0] == '3':
            await interaction.response.send_modal(CheckInfo())


class Verify(discord.ui.Modal, title="인증하기"):
    UserId = discord.ui.TextInput(label="유저의 아이디를 입력하세요", required=True, style=discord.TextStyle.short)
    UserName = discord.ui.TextInput(label="유저의 닉네임을 입력하세요", required=True, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        role = 1149314842327523354
        guild = interaction.guild
        member = guild.get_member(int(self.UserId.value))
        getRole = discord.utils.get(member.guild.roles, id=role)
        await member.add_roles(getRole)
        await member.edit(nick=f"US | {self.UserName.value}")
        
        try:
            embed = discord.Embed(color=0x1a3bc6, title=f"<:dilly:1183243842279985194> 인증이 수락되었어요", description=f"축하합니다! 🎉\n{self.UserName.value}님이 요청하신 인증이 수락되었어요.")
            button = Clickbutton("딜리 이용 시작하기")
            view = discord.ui.View()
            view.add_item(button)
            await member.send(embed=embed, view=view)
            yes = discord.Embed(color=0x1a3bc6, title="인증 완료!", description="인증을 완료했어요!")
            await interaction.response.edit_message(content="인증 완료!",embed=yes, view=None)
        except discord.Forbidden:
            user = await bot.fetch_user(str(751835293924982957))
            await user.send(content=f"{member.name}님에게 메시지 보내기에 실패했어요.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


class CheckInfo(discord.ui.Modal, title="사용자 정보 조회"):
    UserId = discord.ui.TextInput(label="사용자의 디스코드 아이디를 입력하세요", required=True, style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        user_data = db.PayNumber.find_one({"discordId": str(self.UserId.value)})

        if user_data:
            paynumberBar = user_data.get('PayNumberBar')
            paynumber = user_data.get('PayNumber')
            SetName = user_data.get('SetName')
            UserMoney = user_data.get('Money')
            robloxName = user_data.get('PlayerName')
            Dcid = user_data.get('discordName')

            embed = discord.Embed(color=0x1a3bc6, title=f"{SetName}님의 계좌정보")
            embed.add_field(name="> 계좌번호 (-포함)", value=paynumberBar, inline=True)
            embed.add_field(name="> 계좌번호 (-제외)", value=paynumber, inline=True)
            embed.add_field(name="> 예금주 명", value=SetName, inline=True)
            embed.add_field(name="> 계좌 잔액", value=f"{UserMoney}원", inline=True)
            embed.add_field(name="> 로블록스", value=robloxName, inline=True)
            embed.add_field(name="> 디스코드", value=f"<@{self.UserId.value}>", inline=True)
            view = discord.ui.View()
            await interaction.response.edit_message(embed=embed, view=None)

class Clickbutton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, emoji="✨", url="https://discord.com/channels/1149314842327523349/1180858060269436978")



class SendNofi(discord.ui.Modal, title="공지 작성하기"):
    Title = discord.ui.TextInput(label="공지 제목을 입력하세요", required=True, style=discord.TextStyle.short)
    SubTitle = discord.ui.TextInput(label="공지 본문을 입력하세요", required=True, min_length=1, style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        for member in guild.members:
            if member.bot:
                continue

            try:
                embed = discord.Embed(color=0x1a3bc6, title=f"<:dilly:1183243842279985194> {self.Title.value}", description=f"{self.SubTitle.value}")
                await member.send(embed=embed)
                yes = discord.Embed(color=0x1a3bc6, title="공지 전송 완료!", description="공지를 성공적으로 보냈어요.")
                await interaction.response.edit_message(embed=yes, view=None)
            except discord.Forbidden:
                user = await bot.fetch_user(str(751835293924982957))
                await user.send(content=f"{member.name}님에게 메시지 보내기에 실패했어요.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")



class Check(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, emoji="📄")
            
    async def callback(self, interaction):
        user_data = db.PayNumber.find_one({"discordId": str(interaction.user.id)})
        paynumberBar = user_data.get('PayNumberBar')
        paynumber = user_data.get('PayNumber')
        SetName = user_data.get('SetName')
        UserMoney = user_data.get('Money')
        robloxName = user_data.get('PlayerName')
        Dcid = user_data.get('discordName')

        embed = discord.Embed(color=0x1a3bc6, title=f"{SetName}님의 계좌정보")
        embed.add_field(name="> 계좌번호 (-포함)", value=paynumberBar, inline=True)
        embed.add_field(name="> 계좌번호 (-제외)", value=paynumber, inline=True)
        embed.add_field(name="> 예금주 명", value=SetName, inline=True)
        embed.add_field(name="> 계좌 잔액", value=f"{UserMoney}원", inline=True)
        embed.add_field(name="> 로블록스", value=robloxName, inline=True)
        embed.add_field(name="> 디스코드", value=Dcid, inline=True)
        view = discord.ui.View()
        user = await bot.fetch_user(interaction.user.id)
        await user.send(embed=embed)
        await interaction.response.edit_message(content=f"{SetName}님의 다이렉트 메세지로 계좌정보를 보내드렸어요!", view=None)


@bot.tree.command(name="계좌정보확인하기", description="나의 딜리 계좌 정보를 확인할 수 있어요")
async def pay(interaction: discord.Interaction):
    user_data = db.PayNumber.find_one({"discordId": str(interaction.user.id)})  # 컬렉션 이름 수정
    
    if user_data:
        dcId = user_data.get("discordId")
        if dcId == str(interaction.user.id):
            # 사용자 데이터에서 PayNumberBar 필드의 값을 가져옴
            pay_number = user_data.get('PayNumberBar', '계좌번호가 없습니다.')
            # 사용자에게 디렉트 메시지 보내기
            button = Check("계좌 정보 확인하기")
            view = discord.ui.View()
            view.add_item(button)

            await interaction.response.send_message(f"{interaction.user.mention}님의 명의로 개설된 계좌정보를 디엠으로 보내드릴게요.\n`서버 멤버가 보내는 다이렉트 메시지 허용하기`를 활성화 하셨다면,\n아래 버튼을 눌러주세요", view=view , ephemeral=True)
        else:
            await interaction.response.send_message(f"예금주 이외엔 계좌번호를 확인할 수 없어요.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.mention}님의 명의로 개설된 계좌를 찾지 못했어요.", ephemeral=True)


class Cancel(discord.ui.Button):
    def __init__(self, label, rblox):
        super().__init__(label=label, style=discord.ButtonStyle.red, emoji="💥")
        self.rblox = rblox

    async def callback(self, interaction):

        await interaction.response.send_message(f"{self.rblox}님의 인증이 취소되었어요.\n재인증을 시도하시려면, `/딜리계좌만들기` 명령어를 이용해주세요!", ephemeral=True)
        db.verify.delete_one({"PlrName": self.rblox})
        Button.disabled = False

class ChangeNewName(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, emoji="🏷")

    async def callback(self, interaction):
        await interaction.response.send_modal(changeName())

@bot.tree.command(name="딜리계좌개설하기", description="딜리가 제공하는 서비스들을 이용하기 위해선, 딜리 계좌가 필요해요")
async def pay(interaction: discord.Interaction, 로블록스닉네임: str):
    # MongoDB에서 이름으로 검색
    existing_data = db.verify.find_one({"PlrName": 로블록스닉네임})
    user_data = db.PayNumber.find_one({"PlayerName": 로블록스닉네임})
    UserId = interaction.user.id

    if user_data :
        embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description=f"{interaction.user.mention}님의 계정으로 개설된 계좌가 이미 존재합니다.\n계좌번호를 조회하시려면 `/내계좌번호확인하기` 명령어를 이용해주세요!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        dCID = db.PayNumber.find_one({"discordId": str(interaction.user.id)})
        if dCID:
            embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description=f"{interaction.user.mention}님의 계정으로 개설된 계좌가 이미 존재합니다.\n계좌번호를 조회하시려면 `/내계좌번호확인하기` 명령어를 이용해주세요!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if existing_data:
                DcoName = existing_data.get("DiscordName") if existing_data else None
                # 이미 데이터가 존재할 경우 실패 메시지 전송
                embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description=f"{로블록스닉네임}님의 인증은 {DcoName}의 계정의 요청으로 이미 진행중입니다")
                button = Cancel("인증 취소하기", 로블록스닉네임)
                view = discord.ui.View()
                view.add_item(button)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            else:
                # 데이터가 없을 경우 계좌 개설
                data = db.verify.insert_one(
                    {
                        "PlrName": 로블록스닉네임,
                        "DiscordId" : str(interaction.user.id),
                        "DiscordName": interaction.user.name
                    }
                )
                embed = discord.Embed(color=0x1a3bc6, title="딜리 인증 시작하기", description=f"{로블록스닉네임}님의 계좌 개설을 위해 아래 버튼을 클릭하여\n인증을 진행해주세요!")

                button = discord.ui.Button(label="인증하러 가기", style=discord.ButtonStyle.blurple, emoji="✅", url="https://www.roblox.com/games/15503722646/Dilly")
                view = discord.ui.View()
                view.add_item(button)

                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
@bot.tree.command(name="비밀번호찾기", description="비밀번호를 분실하셨나요? 딜리가 찾아드릴게요")
async def password(interaction: discord.Interaction):
    await interaction.response.send_modal(PasswordReset())

@bot.tree.command(name="예금주명변경하기", description="새로운 예금주명으로 변경하실 수 있어요.")
async def password(interaction: discord.Interaction):
    user_data = db.PayNumber.find_one({"discordId": str(interaction.user.id)})

    if user_data :
        setName = user_data.get("SetName")

        embed = discord.Embed(color=0x1a3bc6, title="예금주명을 변경할까요?", description=f"기존 {setName}님의 예금주명을 새로운 예금주명으로 변경할까요?")
        button = ChangeNewName("네 변경할래요")
        view = discord.ui.View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else:
        embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description=f"{interaction.user.mention}님은 아직 딜리계좌가 없는 것 같아요.\n`/딜리계좌개설하기` 명령어를 통해 계좌를 개설하신 후, 다시 시도해주세요")
        await interaction.response.send_message(embed=embed, ephemeral= True)

class changeName(discord.ui.Modal, title="예금주명 변경하기"):
    setNameChange = discord.ui.TextInput(label="변경하실 예금주명을 알려주세요",placeholder="신중하게 선택해주세요", required=True, style=discord.TextStyle.short)
    PayNumberValue = discord.ui.TextInput(label="계좌번호를 알려주세요 (-포함)",placeholder="계좌번호에서 -를 포함해서 입력해주세요", required=True, min_length=15, max_length=15, style=discord.TextStyle.short)


    async def on_submit(self, interaction: discord.Interaction):
        user_data = db.PayNumber.find_one({"PayNumberBar": f"{self.PayNumberValue.value}"})


        if user_data:
            setName = user_data.get("SetName")

            if setName == self.setNameChange.value:
                await interaction.response.send_message("새로 설정할 예금주명과 기존 예금주명이 일치해요. 다른 예금주명을 선택해주세요.", ephemeral= True, delete_after=5)
                return

            # Update the password
            db.PayNumber.update_one(
                {"PayNumberBar": self.PayNumberValue.value},
                {"$set": {"SetName": self.setNameChange.value}}
            )

            embed = discord.Embed(color=0x1a3bc6, title="예금주명이 변경되었습니다", description=f"{self.setNameChange.value}님 명의로 된 계좌의 예금주명이 정상적으로 변경되었습니다")
            embed.add_field(name="기존 이름", value=f"{setName}", inline=True)
            embed.add_field(name="변경된 이름", value=f"{self.setNameChange.value}", inline=True)

            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description="입력한 정보로 계좌정보를 불러올수 없어요.\n계좌번호에 오타가 있는지 확인해주세요")
            embed.add_field(name="변경하시려던 예금주명", value=f"{self.setNameChange.value}", inline=True)
            embed.add_field(name="입력하신 계좌번호", value=f"{self.PayNumberValue.value}", inline=True)
            await interaction.response.edit_message(embed=embed, view=None)


class PasswordReset(discord.ui.Modal, title="딜리계좌 비밀번호 찾기"):
    user_name = discord.ui.TextInput(label="로블록스 닉네임을 알려주세요",placeholder="디스플레이 닉네임X", required=True, min_length=2, style=discord.TextStyle.short)
    user_paynumber = discord.ui.TextInput(label="계좌번호를 알려주세요 (-포함)",placeholder="계좌번호에서 -를 포함해서 입력해주세요", required=True, min_length=15, max_length=15, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = db.PayNumber.find_one({"PlayerName": f"{self.user_name.value}"})


        if user_data:
            get_PayNumber = db.PayNumber.find_one({"PayNumberBar": f"{self.user_paynumber.value}"})

            if get_PayNumber :
                discord_Id = user_data.get("discordId")
                rbloxId = user_data.get("PlayerName")

                await interaction.response.send_message(content="계좌를 만들 때, 인증된 디스코드 계정 디엠으로 인증 확인 메세지를 보내드렸어요.", ephemeral= True)
                embed = discord.Embed(color=0x1a3bc6, title="딜리계좌 인증요청", description=f"계좌 비밀번호 변경 요청이 들어왔습니다.\n요청을 보내신 분이 본인이시라면 '네, 제가 맞습니다'버튼을 눌러주세요.")

                button = verify("네, 제가 맞습니다")
                view = discord.ui.View()
                view.add_item(button)

                user = await bot.fetch_user(discord_Id)
                await user.send(embed=embed, view=view)
            else:
                embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description="입력한 정보로 계좌정보를 불러올수 없어요.\n닉네임과 계좌번호에 오타가 있는지 확인해주세요")
                embed.add_field(name="입력하신 로블록스 닉네임", value=f"{self.user_name.value}", inline=True)
                embed.add_field(name="입력하신 계좌번호", value=f"{self.user_paynumber.value}", inline=True)
                await interaction.response.send_message(embed=embed, ephemeral= True)
        else:
            embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description="입력한 정보로 계좌정보를 불러올수 없어요.\n닉네임과 계좌번호에 오타가 있는지 확인해주세요")
            embed.add_field(name="입력하신 로블록스 닉네임", value=f"{self.user_name.value}", inline=True)
            embed.add_field(name="입력하신 계좌번호", value=f"{self.user_paynumber.value}", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral= True)


class verify(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, emoji="👤")

    async def callback(self, interaction):
        await interaction.response.send_modal(NewPassword())


class NewPassword(discord.ui.Modal, title="딜리계좌 비밀번호 변경하기"):
    newpas = discord.ui.TextInput(label="변경할 비밀번호를 입력하세요", placeholder="변경할 비밀번호를 입력", required=True, min_length=1, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = db.PayNumber.find_one({"discordId": str(interaction.user.id)})

        if user_data:
            pay_Number = user_data.get("PayNumberBar")
            NickName = user_data.get("PlayerName")
            SetName = user_data.get("SetName")
            print(NickName)

            current_password = user_data.get('Password')

            # Check if the current password matches before updating
            if current_password == self.newpas.value:
                await interaction.response.send_message("현재 비밀번호와 동일한 비밀번호는 사용할 수 없어요.")
                return

            # Update the password
            db.PayNumber.update_one(
                {"PlayerName": NickName},
                {"$set": {"Password": self.newpas.value}}
            )

            embed = discord.Embed(color=0x1a3bc6, title="비밀번호가 변경되었습니다", description=f"{NickName}님의 딜리계좌 비밀번호가 정상적으로 변경되었습니다")
            embed.add_field(name="예금주", value=f"{SetName}", inline=True)
            embed.add_field(name="계좌번호", value=f"{pay_Number}", inline=True)
            embed.add_field(name="비밀번호", value=f"{self.newpas.value}", inline=True)
            embed.add_field(name="예금주 닉네임", value=f"{NickName}", inline=True)
            
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.send_message("사용자 데이터를 찾을 수 없습니다.")

@bot.tree.command(name="송금하기", description="송금하시려는 분이 딜리뱅크를 이용하고 계신다면, 디스코드에서 송금할 수 있어요")
async def pay(interaction: discord.Interaction):
    user_data = db.PayNumber.find_one({"discordId": str(interaction.user.id)})

    if user_data :
        await interaction.response.send_modal(alreadySend())
    else:
        embed = discord.Embed(colour=discord.Colour.red(), title="오류가 발생했어요", description=f"{interaction.user.mention}님은 아직 딜리계좌가 없는 것 같아요.\n`/딜리계좌개설하기` 명령어를 통해 계좌를 개설하신 후, 다시 시도해주세요")

        await interaction.response.send_message(embed=embed, ephemeral= True)



class alreadySend(discord.ui.Modal, title="딜리계좌로 송금하기"):
    payNumber = discord.ui.TextInput(label="어떤 계좌로 돈을 보낼까요?", placeholder="계좌번호 입력 (-포함)", required=True, min_length=15, max_length=15, style=discord.TextStyle.short)
    howMoney = discord.ui.TextInput(label="얼마를 보낼까요?", placeholder="숫자 입력", required=True, min_length=1, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        Send_User = db.PayNumber.find_one({"discordId": str(interaction.user.id)})
        To_User = db.PayNumber.find_one({"PayNumberBar": self.payNumber.value})

        def is_number(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        if not is_number(self.howMoney.value):
            embed = discord.Embed(color=0x1a3bc6, title="오류가 발생했어요", description="금액은 숫자로만 입력해주세요.")
            await interaction.response.send_message(embed=embed, view=None, ephemeral=True)
            return

        if To_User:
            pay_Number = To_User.get("PayNumberBar")
            SetName = To_User.get("SetName")
            To_DiscordId = To_User.get("discordId")
            To_money = To_User.get("Money")
            money = self.howMoney.value

            Sd_Money = Send_User.get("Money")
            Sd_Name = Send_User.get("SetName")
            Sd_DiscordId = Send_User.get("discordId")
            Sd_PayNumber = Send_User.get("PayNumberBar")
            Sd_Money_Money = int(Sd_Money) - int(money)
            To_Money_Money = int(To_money) + int(money)

            # Check if the current password matches before updating
# ...

            if int(Sd_Money) >= int(money):
            # Ensure that the remaining balance after withdrawal is not negative
                if Sd_Money_Money >= 0:
                    db.PayNumber.update_one(
                        {"discordId": str(interaction.user.id)},
                        {"$set": {"Money": Sd_Money_Money}}
                    )

                    db.PayNumber.update_one(
                        {"PayNumberBar": self.payNumber.value},
                        {"$set": {"Money": To_Money_Money}}
                    )

                    embed = discord.Embed(color=0x1a3bc6, title=f"{SetName}님에게 {money}원 송금완료!")
                    embed.add_field(name="보내시는 분", value=Sd_Name, inline=True)
                    embed.add_field(name="받는 분", value=SetName, inline=True)
                    embed.add_field(name="보낸 금액", value=f"{money}원", inline=True)

                    toEmbed = discord.Embed(color=0x1a3bc6, title=f"{Sd_Name}님이 내 계좌로 {money}원을 보냈어요", description=f"남은 잔액 : {To_Money_Money}")
                    SdEmbed = discord.Embed(color=0x1a3bc6, title=f"{SetName}님에게 {money}원을 보냈어요", description=f"남은 잔액 : {Sd_Money_Money}")

                    user = await bot.fetch_user(To_DiscordId)
                    Sduser = await bot.fetch_user(Sd_DiscordId)
                    await user.send(embed=toEmbed)
                    await Sduser.send(embed=SdEmbed)
                    await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

                else:
                    embed = discord.Embed(color=0x1a3bc6, title="오류가 발생했어요", description="계좌의 잔액이 부족해요.")
                    await interaction.response.send_message(embed=embed, view=None, ephemeral=True)
            else:
                embed = discord.Embed(color=0x1a3bc6, title="오류가 발생했어요", description="계좌의 잔액이 부족해요.")
                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

# ...

        else:
            embed = discord.Embed(color=0x1a3bc6, title="오류가 발생했어요", description="존재하지 않는 계좌번호 입니다.\n송금하시려는 계좌번호를 다시한번 확인해주세요")
            await interaction.response.send_message(embed=embed, view=None, ephemeral=True)





as_token = os.environ['BOT_TOKEN']
bot.run(as_token)
