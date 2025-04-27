import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from .models import Slot

class SlotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        current_time = now()

        # Fetch the active slot where current time falls between start and end time
        slot = Slot.objects.filter(
            start_time__lte=current_time, 
            end_time__gte=current_time, 
            is_booked=True
        ).first()

        if slot:
            data = {
                "start_time": slot.start_time.strftime('%Y-%m-%d %H:%M'),
                "end_time": slot.end_time.strftime('%Y-%m-%d %H:%M'),
                "teacher": slot.teacher.name if slot.teacher else "Unassigned",
                "booked_by": slot.booked_by.username if slot.booked_by else "Unknown",
            }
            await self.send(text_data=json.dumps(data))
        else:
            await self.send(text_data=json.dumps({"message": "No active slot"}))
