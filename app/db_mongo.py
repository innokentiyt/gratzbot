import time
from pymongo import MongoClient
from app.db_abstract import AbstractDatabase
from app.user import GUser


class MongoDatabase(AbstractDatabase):
    def __init__(self):
        host = '127.0.0.1'
        port = 27017
        db_user = ''
        db_password = ''
        auth_source_db = ''
        db_name = 'gratzbot'
        users_collection_name = 'GUsers'
        bank_collection_name = 'Bank'

        db = MongoClient(f'{host}:{port}',
                        username=db_user,
                        password=db_password,
                        authSource=auth_source_db).get_database(db_name)

        self.users_collection = db.get_collection(users_collection_name)
        self.bank_collection = db.get_collection(bank_collection_name)

    def get_user(self, user_id: str, user_name: str) -> GUser:
        user = self.users_collection.find_one({'_id': user_id})
        print(f'getting user {user_id}, value: {user}')
        if not user:
            print('user not exist, creating user...')
            user = self.create_user(user_id, user_name)
            print(f'created user: {user}')
        
        if 'gold' not in user:
            user['gold'] = 0
        
        result = GUser(
            user_id=user_id,
            name=user_name,
            gold=user['gold'],
            farm=user['farm'],
            saved_date=user['saved_date']
        )
        return result

    def update_user(self, user: GUser) -> None:
        self.users_collection.update_one(
            filter={'_id': user.user_id},
            update={
                '$set': {
                    'name': user.name,
                    'gold': user.gold,
                    'farm': user.farm,
                    'saved_date': user.saved_date
                }
            },
            upsert=False
        )

    def create_user(self, user_id: str, name: str) -> dict[str, any]:
        current_timestamp = int(time.time())
        user_data = {
            '_id': user_id,
            'name': name,
            'gold': 5,
            'farm': 1,
            'saved_date': current_timestamp
        }
        self.users_collection.insert_one(user_data)
        return user_data

    def set_user_data(self, user: GUser) -> None:
        value = {
            '_id': user.user_id,
            'name': user.name,
            'gold': user.gold,
            'farm': user.farm,
            'saved_date': user.saved_date
        }
        self.users_collection.replace_one(value)

    def get_all_users(self) -> dict[str, dict[str, any]]:
        _dict = {}
        for doc in self.users_collection.find():
            _dict[doc['_id']] = {
                'user_id': doc['_id'],
                'name': doc['name'],
                'gold': doc['gold'],
                'farm': doc['farm'],
                'saved_date': doc['saved_date']
            }
        return _dict

    def set_gold_in_bank(self, gold: int) -> None:
        self.bank_collection.update_one(
            filter={'_id': 'gold'},
            update={'$set': {'amount': gold}},
            upsert=True
        )

    def get_gold_from_bank(self) -> int:
        gold = self.bank_collection.find_one({'_id': 'gold'})
        if not gold:
            self.set_gold_in_bank(0)
            return 0
        return int(gold['amount'])
