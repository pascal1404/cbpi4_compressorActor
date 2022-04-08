import logging
import asyncio
from cbpi.api import parameters, Property, CBPiActor
from cbpi.api import *

logger = logging.getLogger(__name__)

@parameters([Property.Select(label="GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]), 
             Property.Select(label="Inverted", options=["Yes", "No"],description="No: Active on high; Yes: Active on low"),
             Property.Number(label="delay_time", configurable=True,description="Time in minutes of the switch-on-delay")])
class CompressorGPIOTimedActor(CBPiActor):

    def get_GPIO_state(self, state):
        # ON
        if state == 1:
            return 1 if self.inverted == False else 0
        # OFF
        if state == 0:
            return 0 if self.inverted == False else 1

    async def on_start(self):
        self.gpio = self.props.GPIO
        self.inverted = True if self.props.get("Inverted", "No") == "Yes" else False
        self.delayTime = int(self.props.get("delay_time", 10))
        self.timer = 0
        GPIO.setup(self.gpio, GPIO.OUT)
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.reqstate = False
        self.state = False

    async def on(self, power=0):
        logger.info("ACTOR %s ON - GPIO %s " %  (self.id, self.gpio))
        if self.timer < int(float(self.delayTime * 60)):
            self.reqstate = True
        else:
            self.reqstate = False
            GPIO.output(self.gpio, self.get_GPIO_state(1))
            self.state = True
            await self.cbpi.actor.timeractor_update(self.id, self.timer)

    async def off(self):
        logger.info("ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        self.timer = 0
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False
        await self.cbpi.actor.timeractor_update(self.id, self.timer)

    def get_state(self):
        return self.state
    
    async def run(self):
        while self.running == True:
            if self.timer < int(float(self.delayTime * 60)):
                self.timer += 1
                await self.cbpi.actor.timeractor_update(self.id, self.timer)
            else:
                if self.reqstate:
                    self.state = True
                    self.reqstate = False
                    GPIO.output(self.gpio, self.get_GPIO_state(1))
                    await self.cbpi.actor.timeractor_update(self.id, self.timer)
            await asyncio.sleep(1)


@parameters([Property.Text(label="Topic", configurable=True, description = "MQTT Topic"),
             Property.Number(label="delay_time", configurable=True,description="Time in minutes of the switch-on-delay")])
class CompressorMQTTTimedActor(CBPiActor):

    async def on_start(self):
        self.topic = self.props.get("Topic", None)
        self.delayTime = int(self.props.get("delay_time", 5))
        self.timer = 0
        self.power = 100
        self.reqstate = False
        self.state = False

    async def on(self, power=0):
        if self.timer < int(float(self.delayTime * 60)):
            self.reqstate = True
        else:
            self.reqstate = False
            await self.cbpi.satellite.publish(self.topic, json.dumps(
                    {"state": "on", "power": self.power, "timer": self.timer}), True)
            self.state = True
            await self.cbpi.actor.timeractor_update(self.id, self.timer)

    async def off(self):
        self.timer = 0
            await self.cbpi.satellite.publish(self.topic, json.dumps(
                    {"state": "off", "power": self.power, "timer": self.timer}), True)
        self.state = False
        await self.cbpi.actor.timeractor_update(self.id, self.timer)

    def get_state(self):
        return self.state
    
    async def run(self):
        while self.running == True:
            if self.timer < int(float(self.delayTime * 60)):
                self.timer += 1
                await self.cbpi.actor.timeractor_update(self.id, self.timer)
            else:
                if self.reqstate:
                    self.state = True
                    self.reqstate = False
                    await self.cbpi.satellite.publish(self.topic, json.dumps(
                            {"state": "on", "power": self.power, "timer": self.timer}), True)
                    await self.cbpi.actor.timeractor_update(self.id, self.timer)
            await asyncio.sleep(1)

def setup(cbpi):
    cbpi.plugin.register("Compressor GPIO", CompressorGPIOTimedActor)
    cbpi.plugin.register("Compressor MQTT", CompressorMQTTTimedActor)
