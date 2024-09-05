import asyncio
from bleak import BleakClient, BleakScanner

from PyObjCTools import AppHelper
from Foundation import *
from CoreBluetooth import *
import objc

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "87654321-4321-8765-4321-fedcba987654"

# Client side code (unchanged)
async def run_ble_client(address):
    async with BleakClient(address) as client:
        print(f"Connected to: {address}")

        value = await client.read_gatt_char(CHARACTERISTIC_UUID)
        print(f"Received: {value.decode()}")

        await client.write_gatt_char(CHARACTERISTIC_UUID, b"Hello from Mac Client!")
        print("Sent: Hello from Mac Client!")

async def client_main():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"Found device: {d.name} ({d.address})")

    target_address = "XX:XX:XX:XX:XX:XX"  # Replace with server's address
    await run_ble_client(target_address)

# Server side code (corrected)
class BluetoothServerDelegate(NSObject):
    def init(self):
        self = objc.super(BluetoothServerDelegate, self).init()
        if self is None: return None
        self.message = "Hello from Mac Server!"
        return self

    def start_advertising(self):
        manager = CBPeripheralManager.alloc().initWithDelegate_queue_(self, None)
        self.manager = manager

    def peripheralManagerDidUpdateState_(self, peripheral):
        if peripheral.state() == CBManagerStatePoweredOn:
            print("Bluetooth is powered on")
            self.add_services()

    def add_services(self):
        service = CBMutableService.alloc().initWithType_primary_(
            CBUUID.UUIDWithString_(SERVICE_UUID), True
        )
        characteristic = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(
            CBUUID.UUIDWithString_(CHARACTERISTIC_UUID),
            CBCharacteristicPropertyRead | CBCharacteristicPropertyWrite | CBCharacteristicPropertyNotify,
            None,
            CBAttributePermissionsReadable | CBAttributePermissionsWriteable
        )
        service.setCharacteristics_([characteristic])
        self.manager.addService_(service)
        self.characteristic = characteristic

    def peripheralManager_didAddService_error_(self, peripheral, service, error):
        if error:
            print(f"Error adding service: {error}")
        else:
            print("Service added successfully")
            self.manager.startAdvertising_({
                CBAdvertisementDataServiceUUIDsKey: [CBUUID.UUIDWithString_(SERVICE_UUID)]
            })

    def peripheralManagerDidStartAdvertising_error_(self, peripheral, error):
        if error:
            print(f"Error advertising: {error}")
        else:
            print("Advertising started successfully")

    def peripheralManager_didReceiveReadRequest_(self, peripheral, request):
        if request.characteristic().UUID() == CBUUID.UUIDWithString_(CHARACTERISTIC_UUID):
            request.setValue_(self.message.encode())
            peripheral.respondToRequest_withResult_(request, CBATTErrorSuccess)
            print("Read request handled")

    def peripheralManager_didReceiveWriteRequests_(self, peripheral, requests):
        for request in requests:
            if request.characteristic().UUID() == CBUUID.UUIDWithString_(CHARACTERISTIC_UUID):
                self.message = str(request.value().bytes().tobytes(), 'utf-8')
                print(f"Received write request: {self.message}")
        peripheral.respondToRequest_withResult_(requests[0], CBATTErrorSuccess)

def run_server():
    delegate = BluetoothServerDelegate.alloc().init()
    delegate.start_advertising()
    AppHelper.runConsoleEventLoop()

def main():
    mode = input("Enter 'client' or 'server': ").strip().lower()
    if mode == 'client':
        asyncio.run(client_main())
    elif mode == 'server':
        run_server()
    else:
        print("Invalid mode. Please enter 'client' or 'server'.")

if __name__ == "__main__":
    main()
