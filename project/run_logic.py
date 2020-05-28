from project.main.services.logic import sensor_data_handling
from project.main.services.logic import logic_status
import asyncio


if __name__ == '__main__':
    logic_status.main()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sensor_data_handling.main(loop))
    loop.close()


