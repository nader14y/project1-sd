from app_log import AppLog
import traceback

AppLog.setup()
logger = AppLog.get("Test")

while True:
    age = input("enter your age: ")
    try:
        if int(age) < 18:
            raise Exception("Age should be greater than 18")

        break
    except ValueError as e:
        logger.error(f"Value Error: {str(traceback.format_exc())}")
    except Exception as e:
        logger.error(e)
        print("Enter valid number")