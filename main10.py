import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from PyObjCTools import AppHelper
from Foundation import *
from CoreBluetooth import *
import objc

import time

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef1"
CHARACTERISTIC_UUID = "87654321-4321-8765-4321-fedcba987654"

# Client side code (updated with more debugging)
def device_found(device: BLEDevice, advertisement_data: AdvertisementData):
    print(f"Found device: {device.name} ({device.address})")
    print(f"  RSSI: {device.rssi}")
    print(f"  Metadata: {device.metadata}")
    print(f"  Advertisement Data: {advertisement_data}")
    if SERVICE_UUID.lower() in [str(uuid).lower() for uuid in advertisement_data.service_uuids]:
        print(f"  ** This device is advertising our service UUID **")

async def run_ble_client(address):
    try:
        async with BleakClient(address) as client:
            print(f"Connected to: {address}")

            # services = client.get_services()
            # for service in services:
                # print(f"Service: {service}")
                # for char in service.characteristics:
                    # print(f"  - Characteristic: {char}")

            value = await client.read_gatt_char(CHARACTERISTIC_UUID)
            print(f"Read Initial State: {value.decode()}")

            new_value = "PTA Threshold: 40dB!"
            await client.write_gatt_char(CHARACTERISTIC_UUID,
                new_value.encode("utf-8"), response=True)
            print(f"Write new state: {new_value}")

            value = await client.read_gatt_char(CHARACTERISTIC_UUID)
            print(f"Confirm Read New State: {value.decode()}")

            await asyncio.sleep(10.0)
    except Exception as e:
        print(f"Error in client: {e}")

async def client_main():
    print("Scanning for Bluetooth devices...")
    scanner = BleakScanner(
        # detection_callback=device_found)
        detection_callback=device_found,
        service_uuids=[SERVICE_UUID])
    await scanner.start()
    await asyncio.sleep(10.0)
    await scanner.stop()

    #devices = await scanner.get_discovered_devices()
    devices = scanner.discovered_devices
    if not devices:
        print("No devices found. Make sure the server is running and advertising.")
        return
    if True:
        for i, device in enumerate(devices):
            print (f"Device {i}: {device.name}"
                f" // {device.metadata.get('uuids', [])} // ({device.address})")

    assert len(devices) == 1
    print ('Connecting to addr: ', devices[0].address)
    # await run_ble_client(devices[0].address)
    addr = "8C:85:90:2F:7B:A8"
    await run_ble_client(addr)
    time.sleep(10)

    return
    for d in devices:
        if "F4C" in d.address:
            breakpoint()
        print(f"Found server device: {d.name} // {d.metadata.get('uuids', [])} // ({d.address})")
        if SERVICE_UUID.lower() in [str(uuid).lower() for uuid in d.metadata.get('uuids', [])]:
            print(f"Found correct server device: {d.name} ({d.address})")
            await run_ble_client(d.address)
            return

    print("Server device not found. Make sure it's running and advertising.")

# Server side code (updated with more debugging)
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
        states = ['Unknown', 'Resetting', 'Unsupported', 'Unauthorized', 'PoweredOff', 'PoweredOn']
        print(f"Bluetooth state changed: {states[peripheral.state()]}")
        if peripheral.state() == CBManagerStatePoweredOn:
            print("Bluetooth is powered on")
            self.add_services()
        else:
            print("Bluetooth is not ready. Please check your Bluetooth settings.")

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
        print(f"Added service: {SERVICE_UUID}")
        print(f"Added characteristic: {CHARACTERISTIC_UUID}")

    def peripheralManager_didAddService_error_(self, peripheral, service, error):
        if error:
            print(f"Error adding service: {error}")
        else:
            print("Service added successfully")
            self.manager.startAdvertising_({
                CBAdvertisementDataServiceUUIDsKey: [CBUUID.UUIDWithString_(SERVICE_UUID)],
                CBAdvertisementDataLocalNameKey: "MacBook BLE Server"
            })
            print(f"Started advertising with UUID: {SERVICE_UUID}")

    def peripheralManagerDidStartAdvertising_error_(self, peripheral, error):
        if error:
            print(f"Error advertising: {error}")
        else:
            print("Advertising started successfully")

    def peripheralManager_didReceiveReadRequest_(self, peripheral, request):
        if request.characteristic().UUID() == CBUUID.UUIDWithString_(CHARACTERISTIC_UUID):
            request.setValue_(self.message.encode())
            peripheral.respondToRequest_withResult_(request, CBATTErrorSuccess)
            print(f"Read request handled with {self.message}")

    def peripheralManager_didReceiveWriteRequests_(self, peripheral, requests):
        print (f"received write request")
        for request in requests:
            if request.characteristic().UUID() == CBUUID.UUIDWithString_(CHARACTERISTIC_UUID):
                self.message = str(request.value().bytes().tobytes(), 'utf-8')
                print(f"Received write request: {self.message}")
        peripheral.respondToRequest_withResult_(requests[0], CBATTErrorSuccess)

def run_server():
    delegate = BluetoothServerDelegate.alloc().init()
    delegate.start_advertising()
    print("Server started. Press Ctrl+C to stop.")
    try:
        AppHelper.runConsoleEventLoop()
    except KeyboardInterrupt:
        print("Server stopped.")

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
