from project.main.services.logic import SensorDataHandling
from project.main.services.logic import LogicStatus
import asyncio


if __name__ == '__main__':
    LogicStatus.main()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SensorDataHandling.main(loop))

