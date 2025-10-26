import asyncio
from bleak import BleakScanner, BleakClient
import datetime
import json

# ---------------- Health Analyzer ---------------- #
class HealthAnalyzer:
    def __init__(self, sleep_hours, deep_sleep, rem_sleep, heart_rate,
                 screen_time, pickups, breaks,
                 meals, nutrition_goals, supplements):
        self.sleep_hours = sleep_hours
        self.deep_sleep = deep_sleep
        self.rem_sleep = rem_sleep
        self.heart_rate = heart_rate
        self.screen_time = screen_time
        self.pickups = pickups
        self.breaks = breaks
        self.meals = meals
        self.nutrition_goals = nutrition_goals
        self.supplements = supplements

    def analyze_sleep(self):
        score = 100
        if self.sleep_hours < 7: score -= 20
        if self.deep_sleep < 1.5: score -= 10
        if self.heart_rate > 70: score -= 5
        return {
            "hours": self.sleep_hours,
            "deep": self.deep_sleep,
            "rem": self.rem_sleep,
            "score": score,
            "quality": "Good" if score > 70 else "Poor"
        }

    def analyze_screen_time(self):
        score = max(0, 100 - (self.screen_time - 4) * 10)
        return {
            "screen_time": self.screen_time,
            "pickups": self.pickups,
            "breaks": self.breaks,
            "score": score
        }

    def analyze_nutrition(self):
        report = {}
        for nutrient, goal in self.nutrition_goals.items():
            val = self.meals.get(nutrient, 0)
            report[nutrient] = {
                "intake": val,
                "goal": goal,
                "status": "ok" if val >= goal * 0.8 else "low"
            }
        return report

    def recommend_supplements(self):
        recs = []
        if self.sleep_hours < 7:
            recs.append("Magnesium for better sleep")
        if self.meals.get("protein", 0) < self.nutrition_goals.get("protein", 50):
            recs.append("Protein supplement")
        if self.screen_time > 6:
            recs.append("Vitamin A for eye health")
        return recs

    def daily_summary(self):
        return {
            "date": datetime.date.today().isoformat(),
            "sleep": self.analyze_sleep(),
            "screen": self.analyze_screen_time(),
            "nutrition": self.analyze_nutrition(),
            "supplement_recommendations": self.recommend_supplements()
        }

# ---------------- Bluetooth Data Manager ---------------- #
class BluetoothManager:
    """
    Scans for Bluetooth devices and retrieves basic health metrics
    (like heart rate, etc.) from a connected device.
    """

    HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # standard Heart Rate characteristic UUID

    async def scan_devices(self, timeout=5.0):
        """Scan for available Bluetooth devices."""
        devices = await BleakScanner.discover(timeout=timeout)
        result = [{"name": d.name or "Unknown", "address": d.address} for d in devices]
        return result

    async def connect_and_retrieve(self, address):
        """
        Connect to a specific Bluetooth device and read heart rate or other available data.
        Returns a dictionary of sensor readings.
        """
        data = {"heart_rate": None, "device": address, "status": "disconnected"}
        try:
            async with BleakClient(address) as client:
                if client.is_connected:
                    data["status"] = "connected"
                    # try reading heart rate characteristic
                    try:
                        raw = await client.read_gatt_char(self.HR_UUID)
                        if len(raw) > 1:
                            flags = raw[0]
                            hr = int.from_bytes(raw[1:3], "little") if (flags & 0x01) else raw[1]
                            data["heart_rate"] = hr
                    except Exception:
                        pass
        except Exception as e:
            data["error"] = str(e)
        return data

# ---------------- Main Backend Logic ---------------- #
class HealthBackend:
    """
    This class combines Bluetooth retrieval and analysis.
    The frontend/chatbot can call its methods to get updated data.
    """

    def __init__(self):
        self.bt_manager = BluetoothManager()

    async def scan_devices(self):
        """Return list of scanned devices."""
        return await self.bt_manager.scan_devices()

    async def retrieve_and_analyze(self, address):
        """
        Connects to a Bluetooth device, retrieves sensor data,
        and performs full analysis. Returns JSON-compatible dict.
        """
        bt_data = await self.bt_manager.connect_and_retrieve(address)
        hr = bt_data.get("heart_rate") or 70  # fallback HR
        # Example placeholder values; can be replaced with real sensor metrics
        analyzer = HealthAnalyzer(
            sleep_hours=6.5,
            deep_sleep=1.2,
            rem_sleep=1.5,
            heart_rate=hr,
            screen_time=6,
            pickups=40,
            breaks=3,
            meals={"calories": 1800, "protein": 60, "carbs": 220, "fat": 65},
            nutrition_goals={"calories": 2000, "protein": 80, "carbs": 250, "fat": 70},
            supplements=[]
        )
        analysis = analyzer.daily_summary()
        return {
            "bluetooth_data": bt_data,
            "analysis": analysis
        }

# ---------------- Example CLI Test ---------------- #
if __name__ == "__main__":
    async def main():
        backend = HealthBackend()
        print("Scanning for Bluetooth devices...")
        devices = await backend.scan_devices()
        print(json.dumps(devices, indent=2))

        if not devices:
            print("No devices found.")
            return

        # Connect to first found device (for testing)
        address = devices[0]["address"]
        print(f"\nConnecting to {address} ...")
        results = await backend.retrieve_and_analyze(address)
        print(json.dumps(results, indent=2))

    asyncio.run(main())
