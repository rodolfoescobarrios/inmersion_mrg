# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"room_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"Mensaje recibido en el servidor: {text_data}")

        try:
            text_data_json = json.loads(text_data)

            if 'action' in text_data_json:
                action = text_data_json['action']
                time = text_data_json.get('time', None)

                if action not in ['play', 'pause', 'seek']:
                    raise ValueError(f"Acción inválida recibida: {action}")

                if action == 'seek' and (time is None or not isinstance(time, (int, float))):
                    raise ValueError(f"Tiempo inválido para la acción 'seek': {time}")

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'video_action',
                        'action': action,
                        'time': time
                    }
                )

            elif 'message' in text_data_json:
                message = text_data_json['message']

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message
                    }
                )
            else:
                raise ValueError("Mensaje recibido sin 'action' o 'message'.")

        except ValueError as e:
            print(f"Error de validación: {e}")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            await self.close()
        except Exception as e:
            print(f"Error inesperado: {e}")
            await self.close()

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def video_action(self, event):
        action = event['action']
        time = event.get('time', None)
        await self.send(text_data=json.dumps({
            'action': action,
            'time': time
        }))
