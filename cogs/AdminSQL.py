import asyncio
import datetime
import random
import sqlite3
from nextcord.ext import commands, tasks, application_checks
from nextcord.ui import Button, View
from config import *
import nextcord
from colorama import init, Fore

connection1 = sqlite3.connect('data/database/economy.db')
cursor2 = connection1.cursor()

logo2 = '''                                        
 .-------:      :-====--.     .---          
=++++====-    -+++++==++++-   :+++          
=++=        .++++:     :+++=  :+++          
 =+++-.     +++=         +++- :+++          
  :++++=.   +++:         =++= :+++          
    .=+++-  +++=         +++- :+++          
      :+++. .+++=: =++..=+++  :+++-.        
=++++++++=    -+++ =++++++-   .+++++++.     
-------:.       .- =++=-:       :-----.     
                          =++.              
                                            
SQLite3 Manager for discord.                
'''


class RequestSQL(nextcord.ui.Modal):
    def __init__(self):
        self.connection = connection1
        self.cursor = cursor2
        super().__init__('Запрос по базе данных')

        self.RequestSQL = nextcord.ui.TextInput(label='Введите запрос', max_length=500, required=True,
                                               placeholder='SELECT...', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.RequestSQL)


    async def callback(self, interaction: nextcord.Interaction) -> None:
        request = self.RequestSQL.value

        try:
            self.cursor.execute(request)
            results = self.cursor.fetchall()

            embed = nextcord.Embed(title='Запрос по базе данных',
                                description='Результат:\n```{}```'.format(results),
                                color=0x008000)
            embed.set_thumbnail(url=interaction.user.avatar)
            await interaction.send(embed=embed, ephemeral=True)
        except sqlite3.OperationalError as e:
            embed = nextcord.Embed(title='Ошибка в запросе',
                                description='Результат:\n```{}```'.format(str(e)),
                                color=0xFF0000)
            embed.set_thumbnail(url=interaction.user.avatar)
            await interaction.send(embed=embed, ephemeral=True)

class CreateTable2(nextcord.ui.Modal):
    def __init__(self, table):
        self.connection = connection1
        self.cursor = cursor2
        super().__init__('Запрос DB')

        self.CreateTable2 = nextcord.ui.TextInput(label='Введите название ключа', max_length=25, required=True,
                                               placeholder='key...', style=nextcord.TextInputStyle.paragraph)
        self.table = table 

        self.add_item(self.CreateTable2)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        key = self.CreateTable2.value

        self.cursor.execute(f'''
            CREATE TABLE {self.table} (
                {key} TEXT
            );
        ''')
        
        print(f'{self.table}, {key}')

class DeleteKey(nextcord.ui.Modal):
    def __init__(self, table):
        self.connection = connection1
        self.cursor = cursor2
        super().__init__('Удалить ключ')

        self.DeleteKey = nextcord.ui.TextInput(label='Название ключа', max_length=25, required=True,
                                               placeholder='key...', style=nextcord.TextInputStyle.paragraph)
        self.table = table 

        self.add_item(self.DeleteKey)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        key = self.DeleteKey.value

        self.cursor.execute(f'ALTER TABLE `{self.table}` DROP COLUMN `{key}`;')
        self.connection.commit()
        
        await interaction.response.send_message('Ключ `{}` успешно удалён'.format(key), ephemeral=True)

class CreateKey(nextcord.ui.Modal):
    def __init__(self, table):
        self.connection = connection1
        self.cursor = cursor2
        super().__init__('Создать ключ')

        self.CreateKey = nextcord.ui.TextInput(label='Название ключа и тип данных', max_length=50, required=True,
                                               placeholder='НАЗВАНИЕ_КЛЮЧА ТИП_ДАННЫХ...', style=nextcord.TextInputStyle.paragraph)
        self.table = table

        self.add_item(self.CreateKey)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        input_data = self.CreateKey.value.split(' ')
        
        if len(input_data) != 2:
            await interaction.response.send_message('Введите название ключа и тип данных через пробел.', ephemeral=True)
            return

        key_name, data_type = input_data

        try:
            self.cursor.execute(f'ALTER TABLE {self.table} ADD COLUMN {key_name} {data_type};')
            self.connection.commit()
            await interaction.response.send_message(f'Ключ `{key_name}` с типом данных `{data_type}` успешно создан.', ephemeral=True)
        except sqlite3.OperationalError as e:
            await interaction.response.send_message(f'Ошибка при создании ключа: {str(e)}', ephemeral=True)

class CreateTable(nextcord.ui.Modal):
    def __init__(self):
        self.connection = connection1
        self.cursor = cursor2
        super().__init__('Запрос DB')

        self.CreateTable = nextcord.ui.TextInput(label='Введите название таблицы', max_length=25, required=True,
                                               placeholder='Name table...', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.CreateTable)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        table = self.CreateTable.value

        set_key = Button(style=nextcord.ButtonStyle.primary,
                             label='Таблицы')
        
        async def set_key_callback(interaction: nextcord.Interaction):
            create_table_modal = CreateTable2(table)
            await interaction.response.send_modal(create_table_modal)

        set_key.callback = set_key_callback
        view = View(timeout=60)
        view.add_item(set_key)
        
        await interaction.send('Имя задано', view=view, ephemeral=True)

class AdminSQL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = connection1
        self.cursor = cursor2

    @commands.Cog.listener()
    async def on_ready(self):
        init(autoreset=True)
        print(Fore.CYAN + 'Admin' + Fore.YELLOW + 'SQL' + Fore.RESET + ' Lib is Work')
    
    @nextcord.slash_command(name='menu', description='Центр управление базой данных')
    async def menu_sqlite3_lib(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(description='```{}```'.format(logo2),
                               color=0x313338)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_footer(text='Github: github.com/reques6e/AdminSQL')
        
        request = Button(style=nextcord.ButtonStyle.green,
                             label='Запрос')
        tables = Button(style=nextcord.ButtonStyle.primary,
                             label='Таблицы')
        
        async def request_callback(interaction: nextcord.Interaction):
            await interaction.response.send_modal(RequestSQL())
        
        async def tables_callback(interaction: nextcord.Interaction):
            self.cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
            result = self.cursor.fetchall()
            
            table_names = [table[0] for table in result]

            embed = nextcord.Embed(title='Запрос по базе данных',
                                description='Таблицы:\n ```{}```'.format('\n'.join(table_names)),
                                color=0x008000)

            embed.set_thumbnail(url=interaction.user.avatar)
            

            create = Button(style=nextcord.ButtonStyle.green,
                        label='Создать')
            
            view = View(timeout=60)
            async def create_callback(interaction: nextcord.Interaction):
                await interaction.response.send_modal(CreateTable())

            for table_name in table_names:
                button = Button(style=nextcord.ButtonStyle.primary,
                        label=table_name,
                        custom_id=f'table_{table_name}')
                
                async def button_callback(interaction: nextcord.Interaction, table=table_name):
                    self.cursor.execute('SELECT * FROM {}'.format(table))
                    result = self.cursor.fetchall()

                    def get_table_columns(table):
                        self.cursor.execute(f"PRAGMA table_info({table})")
                        columns = self.cursor.fetchall()

                        return columns
                    
                    columns_info = get_table_columns(table)

                    embed = nextcord.Embed(title='Запрос по базе данных',
                                description='Ответ от db:\n ```{}```'.format(result),
                                color=0x008000)
                    
                    for column_info in columns_info:
                        column_name = column_info[1]
                        data_type = column_info[2]
                        embed.add_field(name=column_name, value=data_type, inline=True)

                    embed.set_thumbnail(url=interaction.user.avatar)

                    create_key = Button(style=nextcord.ButtonStyle.green,
                        label='Создать ключ')
                    delete = Button(style=nextcord.ButtonStyle.red,
                        label='Удалить эту таблицу')
                    delete_key = Button(style=nextcord.ButtonStyle.red,
                        label='Удалить ключ',
                        disabled=True)
                    
                    async def create_key_callback(interaction: nextcord.Interaction):
                        crt_key = CreateKey(table)
                        await interaction.response.send_modal(crt_key)

                    async def delete_callback(interaction: nextcord.Interaction, del_table=table):
                        self.cursor.execute(f'DROP TABLE IF EXISTS {table};')
                        self.connection.commit()

                        await interaction.send('Таблица {} успешна удалена!'.format(table), ephemeral=True)
                    
                    async def delete_key_callback(interaction: nextcord.Interaction):
                        delkey = DeleteKey(table)
                        await interaction.response.send_modal(delkey)

                    create_key.callback = create_key_callback
                    delete.callback = delete_callback
                    delete_key.callback = delete_key_callback
                    view = View(timeout=60)
                    view.add_item(create_key)
                    view.add_item(delete_key)
                    view.add_item(delete)
                    await interaction.send(embed=embed, view=view, ephemeral=True)
                
                button.callback = button_callback
                view.add_item(button)

            create.callback = create_callback
            view.add_item(create)
            await interaction.send(embed=embed, view=view, ephemeral=True)



        request.callback = request_callback
        tables.callback = tables_callback
        view = View(timeout=60)
        view.add_item(request)
        view.add_item(tables)
        await interaction.send(embed=embed, view=view)



def setup(bot):
    bot.add_cog(AdminSQL(bot))
