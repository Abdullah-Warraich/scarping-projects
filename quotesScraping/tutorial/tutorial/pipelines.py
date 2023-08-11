# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class TutorialPipeline:
    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = sqlite3.connect("mydb.db")
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""drop table if exists quotes_tb""")
        self.curr.execute("""create table quotes_tb(
                          title text, 
                          author text, 
                          author_link text, 
                          tag text
                          )""")

    def process_item(self, item, spider):
        self.curr.execute("""insert into quotes_tb values (?,?,?,?)""", (item['text'],
                                                                         item['author'],
                                                                         item['author_link'],
                                                                         ', '.join([str(n) for n in item['tags']])))
        self.conn.commit()
        print(item)
        return item
