import json
import os
from pathlib import Path
from datetime import datetime
from django.conf import settings

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from accounts.models import Conversation, User, Message

online_users = dict()

# chat/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_admin_new_message(admin_id, conversation_id, message, sender_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"admin_notify_{admin_id}",
        {
            "type": "admin.message",
            "conversation_id": conversation_id,
            "message": message,
            "sender_id": sender_id,
        }
    )

# Serialization of django queryset
def messages_to_json(messages):
    result = []
    for message in messages:
        result.append({
            'id': message.id,
            'email': message.email,
            'full_name': message.get_full_name(),
            'profile': message.profile.url if message.profile else None
        })
    return result

def storeChat(data, room_name):
    file_path = os.path.join(settings.MEDIA_ROOT, 'chat_log', room_name)

    Path(file_path).mkdir(parents=True, exist_ok=True)

    current_time = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-4]
    file_name = current_time + '.txt'

    try:
        if 'message' in data:
            with open(file_path + '/' + file_name, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        return

    except Exception as e:
        return


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user is None or isinstance(user, AnonymousUser):
            await self.close()
            return

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

    async def disconnect(self, code):
        # Remove user according to room_name
        if self.room_name in online_users.keys():
            online_users[self.room_name].remove(self.scope['user'])



        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Send message to room group when user disconnect
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
        text_data_json = json.loads(text_data)
        sender_id = text_data_json['sender_id']
        sender_name = text_data_json['sender_name']
        sender_icon = text_data_json['sender_icon']
        sender_datetime = text_data_json['sender_datetime']
        # message_type = text_data_json['message_type']
        # if message_type != "studytimeprogress":
        message = text_data_json['message']

        # Calls function to store the chat
        # if message_type == 'chat_message':
        storeChat(text_data_json, self.room_group_name)

        chatData = {
            'type': 'chat_message',
            # 'message_type': message_type,
            'sender_id': sender_id,
            'sender_name': sender_name,
            'sender_icon': sender_icon,
            'sender_datetime': sender_datetime,
            'message': message,
        }
        # message_link_type => determines if message is for quiz or survey. Not present in case of chat messages.
        # if message_link_type present -> 'message' is primary key of quiz or survey
        if 'message_link_type' in text_data_json:
            chatData['message_link_type'] = text_data_json['message_link_type']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            chatData
        )

    async def chat_message(self, event):
        sender_id = event['sender_id']
        sender_name = event['sender_name']
        sender_icon = event['sender_icon']
        sender_datetime = event['sender_datetime']
        message = event['message']
        # Send message to WebSocket
        chatdata = {
            'sender_id': sender_id,
            'sender_name': sender_name,
            'sender_icon': sender_icon,
            'sender_datetime': sender_datetime,
            'message': message,
        }
        # if 'message_link_type' in event:
        #     chatdata['message_link_type'] = event['message_link_type']
        await self.send(text_data=json.dumps(chatdata))

#
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
from channels.db import database_sync_to_async
# from .models import Message, Conversation
# from users.models import User
class ChatConsumerNew(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.conversation_id}'

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = self.scope["user"].id

        await self.save_message(self.conversation_id, sender_id, message)

        conversation = Conversation.objects.get(id=self.conversation_id)
        message_text = message
        if self.scope["user"].user_type.name == "worker":
            notify_admin_new_message(
                admin_id=conversation.admin.id,
                conversation_id=conversation.id,
                message=message_text,
                sender_id=self.scope["user"].id
            )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, conversation_id, sender_id, message):
        conversation = Conversation.objects.get(id=conversation_id)
        sender = User.objects.get(id=sender_id)
        return Message.objects.create(conversation=conversation, sender=sender, content=message)


# admin/consumers.py

class AdminNotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']

        if not user.is_authenticated:
            print("❌ WebSocket rejected: unauthenticated user")
            await self.close()
            return

        if getattr(user, "user_type", None) is None or user.user_type.id != 1:
            print(f"❌ WebSocket rejected: user {user} is not admin")
            await self.close()
            return

        self.group_name = f"admin_notify_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print(f"✅ WebSocket connected for admin_notify_{user.id}")
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        else:
            print("Disconnect without group name")

    async def admin_message(self, event):
        await self.send(text_data=json.dumps({
            "conversation_id": event["conversation_id"],
            "message": event["message"]
        }))
