import json
from channels.generic.websocket import AsyncWebsocketConsumer
online_users = dict()

# Serialization of django queryset
def messages_to_json(messages):
    result = []
    for message in messages:
        result.append({
            'id': message.id,
            # 'email': message.email,
            # 'full_name': message.get_full_name(),
            # 'avatar': message.member_avatar
        })
    return result

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connected")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # New user added according to room_name
        if self.room_name in online_users.keys():
            online_users[self.room_name].append(self.scope['user'])
        else:
            online_users[self.room_name] = [self.scope['user']]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send message to room group on new user addition
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_users',
                'user_list': messages_to_json(set(online_users[self.room_name])),
            }
        )
    async def chat_users(self, event):
            user_list = event['user_list']
            user_count = len(user_list)

            # Send message to WebSocket about users list
            await self.send(text_data=json.dumps({
                'message_type': 'chat_users',
                'user_list': user_list,
                'user_count': user_count
            }))

    async def receive(self, text_data=None, bytes_data=None):
        print("data received")

    async def disconnect(self, code):
        print("user disconnect")
        # Remove user according to room_name
        # if self.room_name in online_users.keys():
        #     online_users[self.room_name].remove(self.scope['user'])