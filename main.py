# import modules from Pyfirmata
from pyfirmata import Arduino , OUTPUT , INPUT , util, PWM
# import inbuilt time module
import time
#import modules
import analogInput
#import mqtt
import paho.mqtt.client as mqtt

# create an Arduino board instance
board = Arduino ("COM3")

group='G17A'
topic = "G17A/CDR/DATA"
topic2="EmergencyState"
topic3="CheckCd"


#setup server
mqttBroker = "vpn.ce.pdn.ac.lk" #Must be connected to the vpn
mqttPort = 8883

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)
    client.subscribe(topic2)
    client.subscribe(topic3)


# The callback for when a PUBLISH message is received from the server.


emergencyStatus=''
accessDoor=''

def on_message(client, userdata, msg):


    if msg.topic=="EmergencyState":
        global emergencyStatus
        emergencyStatus=str(msg.payload)
        print("emer state:", emergencyStatus)
    if msg.topic=="CheckCd":
        global accessDoor
        accessDoor=str(msg.payload)
        print("check cd:",accessDoor)




client = mqtt.Client(group)


try:
    client.connect(mqttBroker,mqttPort)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()
except:
    print("Connection to MQTT broker failed!")
    exit(1)

# analog pin number
therm_pin = 0
ldr_pin =1

# set digital output pins
led_pin_r = 6
led_pin_g = 7
buzzer_pin= 5

# set digital output pins
sw_1= 2
sw_2 = 3
swAct = 8
swCls = 9
doorCls = 10
pressure= 4


# set analog input pins
board . analog[therm_pin]. mode = INPUT
board . analog[ldr_pin]. mode = INPUT

# set digital output pins
board . digital [led_pin_r]. mode = OUTPUT
board . digital [led_pin_g]. mode = OUTPUT
board . digital [buzzer_pin]. mode = PWM

# set digital input pins
board . digital[sw_1].mode = INPUT
board . digital[sw_2].mode = INPUT
board . digital[pressure].mode = INPUT
board . digital[swAct].mode = INPUT
board . digital[swCls].mode = INPUT
board . digital[doorCls].mode = INPUT

print('Initiate Security System')

# start the utilization service
# this service will handle communication overflows while communicating with the Arduino board via USB intrface .
it = util . Iterator ( board )
it . start ()
board . analog [ldr_pin]. enable_reporting ()
board . analog [therm_pin]. enable_reporting ()

def melody():
    board.digital[buzzer_pin].write(1)
    time.sleep(0.1)
    board.digital[buzzer_pin].write(0)


def lockdown():

    board.digital[led_pin_r].write(1)
    board.digital[led_pin_g].write(0)
    board.digital[buzzer_pin].write(1)
    time.sleep(0.5)
    board.digital[led_pin_r].write(0)
    board.digital[buzzer_pin].write(0)
    board.digital[led_pin_g].write(1)
    board.digital[led_pin_g].write(0)
    emergency='on'

def checkAccess(code):

    while accessDoor!="b'Allow'" and accessDoor!="b'Deny'":
        data(board.analog[ldr_pin].read() * 1024, analogInput.temperatureReading(board.analog[therm_pin].read()),presr_sensor, emergency, "Someone Trying To Open Door in CDR!",code)
        print('access:',accessDoor)
        time.sleep(0.5)

def blink():

    board.digital[led_pin_r].write(1)
    time.sleep(0.5)
    board.digital[led_pin_r].write(0)

def data(ldrVal,tempVal,psrState,emergency,data="",code=''):
    data = [str(round(ldrVal, 2)), str(round(tempVal, 2)), str(psrState), str(emergency),data,str(code)]  # array of data
    data = ','.join(data)  # join array of data as a single comma seperated string

    client.publish(topic, data)  # publish the data to MQTT broker using the topic
    print('Sent from Arduino ', data)



#giving access to sensors
ldrAccess='allow'
psrAccess='allow'

door_state='open'
doorState='Closed'

while True :

    ldr_val = board.analog[ldr_pin].read()  # read the ldr value
    therm_val = board.analog[therm_pin].read()  # read the thermistor value
    presr_sensor=board.digital[pressure].read()
    swAct_val = board.digital[swAct].read()
    swCls_val = board.digital[swCls].read()
    sw1_val = board.digital[sw_1].read()
    sw2_val = board.digital[sw_2].read()
    emergency='off'


    if ldr_val==None or therm_val==None or presr_sensor==None or sw_1==None or sw_2==None:
        continue

    ldr_val = ldr_val * 1024
    print('LDR Value: %s \n Therm Value: %s'%(ldr_val,therm_val))

    # Calculate Temperature
    temp= analogInput.temperatureReading(therm_val)

    # Sequence input
    code = []

    cd_confidential = [1,1,1,2]
    cd_secret = [5,4,1,1]
    cd_superSecret = [1,5,3,1]

    if swAct_val == True:
        print('Enter Your Code!')
        melody()
        runTime = 0
        code=[]
        while True:
            #get sw1 readings and add to list

            sw1Val=0
            sw2Val=0
            timeGap=0
            timeGap2= 0
            melody()
            startTime = time.time()
            print('Switch 1 Activated')
            while timeGap<=5.0:
                board.digital[led_pin_r].write(1)
                board.digital[led_pin_g].write(0)
                timeGap=time.time()-startTime
                if board.digital[sw_1].read()==True:
                    sw1Val+=1
                    board.digital[buzzer_pin].write(1)
                    board.digital[buzzer_pin].write(0)
                time.sleep(0.2)

            code.append(sw1Val)

            #get sw2 readings and add to list
            melody()
            startTime = time.time()
            print('Switch 2 Activated')
            while timeGap2<=5.0:
                board.digital[led_pin_r].write(0)
                board.digital[led_pin_g].write(1)
                timeGap2=time.time()-startTime
                if board.digital[sw_2].read()==True:
                    sw2Val+=1
                    board.digital[buzzer_pin].write(1)
                    board.digital[buzzer_pin].write(0)
                time.sleep(0.2)

            code.append(sw2Val)

            if len(code)==4:
                board.digital[led_pin_r].write(0)
                board.digital[led_pin_g].write(0)
                data(board.analog[ldr_pin].read() * 1024,analogInput.temperatureReading(board.analog[therm_pin].read()), presr_sensor, emergency,"Code Entered!",code)
                break

            if board.digital[swCls].read()==True :
                break

        checkAccess(code)
        print(accessDoor)

        if code == cd_confidential and accessDoor=="b'Allow'":
            print('Open For Confidential!!!!!')
            doorState = 'Open For Level Confidential!'
            melody()
            blink()

        elif code == cd_secret and accessDoor=="b'Allow'":
            print('Open For Secret!!!!!')
            doorState = 'Open For Level Secret!'
            psrAccess='deny'
            melody()
            blink()
            melody()
            blink()

        elif code == cd_superSecret and accessDoor=="b'Allow'":
            print('Open For Super Secret!!!!!')
            doorState = 'Open For Level Super Secret!'
            psrAccess='deny'
            ldrAccess='deny'
            melody()
            blink()
            melody()
            blink()
            melody()
            blink()
        else:
            while True:
                print('code:', code)
                print('Unorthorized Enter!!!!!')
                lockdown()
                emergency = 'on'
                data(board.analog[ldr_pin].read()*1024, analogInput.temperatureReading(board.analog[therm_pin].read()), presr_sensor, emergency,"Code Entered Is Wrong")
                if board.digital[swCls].read() == True or emergencyStatus=="b'emergencyOff'":
                    break
        accessDoor=''

    #close door and open door
    if board.digital[doorCls].read()==True:
        if door_state=='open':
            melody()
            door_state='close'
            doorState='Closed!'
            print('Door Closed !')
        elif door_state=='close':
            melody()
            print('Door Open For 10 seconds')
            doorState = 'Open For 10 seconds!'
            data(board.analog[ldr_pin].read() * 1024, analogInput.temperatureReading(board.analog[therm_pin].read()),presr_sensor, emergency,doorState)
            time.sleep(10)
            melody()
            print('Door Closed and All sensors are Activated!')
            doorState = 'Door Closed!'
            data(board.analog[ldr_pin].read() * 1024, analogInput.temperatureReading(board.analog[therm_pin].read()),presr_sensor, emergency, doorState)
            psrAccess='allow'
            ldrAccess='allow'
        time.sleep(0.3)

   # detect fire
    if temp>=40:
        print('Fire!!!!!!!!!!!!!!!!')
        lockdown()
        emergency = 'on'

    # detect unusual light intencity
    if ldr_val>1000 or 200>ldr_val:

        if ldrAccess=='allow':
            print('Light Intencity Is Unusual!!!!!!!!!!')
            lockdown()
            emergency = 'on'

    # pressure sensors
    if presr_sensor==True:

        if psrAccess=='allow':
            print("Unorthorized Entered!!!!!!!!!!!!!")
            lockdown()
            emergency = 'on'
    print(emergencyStatus)

    if emergencyStatus=="b'emergencyOn'":
        lockdown()
        data(board.analog[ldr_pin].read() * 1024, analogInput.temperatureReading(board.analog[therm_pin].read()),presr_sensor, emergency)

    data(ldr_val,temp,presr_sensor, emergency,doorState)

    time.sleep(0.1)

