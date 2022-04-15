import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

# Fetch the service account key JSON file contents
cred = credentials.Certificate('./serviceAccount.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://comp7940project-34c59-default-rtdb.firebaseio.com"
})

ref = db.reference("/Books/item")
data = ref.get()
if data is None:
    print("a is none")
    ref = db.reference("/Books")
    ref.set({
        "review": -1
    })
ref = db.reference("/Books/review")
ref.push().set("aaaaa")
ref.push().set("bbbbb")




# 写到数据库中
# with open("book_info.json", "r") as f:
# 	file_contents = json.load(f)
# ref.set(file_contents)

# Firebase 为我们提供了push()将数据保存在唯一系统生成的密钥下的功能。
# 此方法确保如果对同一个键执行多个写入，它们不会覆盖自己。
# ref = db.reference("/")
# ref.set({
#     "Books":
#         {
#             "Best_Sellers": -1
#         }
# })
#
# ref = db.reference("/Books/Best_Sellers")
#
# with open("book_info.json", "r") as f:
#     file_contents = json.load(f)
#
# for key, value in file_contents.items():
#     ref.push().set(value)
#
# # 修改
# ref = db.reference("/Books/Best_Sellers/")
# best_sellers = ref.get()
# print(best_sellers)
# for key, value in best_sellers.items():
#     if value["Author"] == "J.R.R. Tolkien":
#         value["Price"] = 90
#         ref.child(key).update({"Price": 80})
#
# # 查询
# ref = db.reference("/Books/Best_Sellers/")
# print(ref.order_by_child("Price").get())
# # 该方法的返回值是一个 OrderedDict。要按键排序，请使用order_by_key()。
# ref.order_by_child("Price").limit_to_last(1).get()
# # 要获得准确定价为 80 单位的书籍
# ref.order_by_child("Price").equal_to(80).get()

# 删
# for key, value in best_sellers.items():
#     if value["Author"] == "J.R.R. Tolkien":
#         ref.child(key).set({})
