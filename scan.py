from bleak import BleakClient, BleakScanner
import asyncio
async def main():
    devices = await BleakScanner.discover(timeout=10)
    devices = sorted(devices, key=lambda d: d.rssi, reverse=True)
    for i, d in enumerate(devices):
        print (f"Device {i}: rssi={d.rssi} {d}")
        if d.name is not None and d.name.startswith("ATC_C562B4"):
            print("Connecting to", d)
            client = BleakClient(d, timeout=30)
            try:
                await client.connect()
                print("connected!")

                for service in client.services:
                    for char in service.characteristics:
                        print(char)
            finally:
                print("Disconnecting from", d)
                await client.disconnect()

            break

asyncio.run(main())
