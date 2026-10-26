import sys
from networksecurity.logging.logger import logger


class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details):
        super().__init__(str(error_message))

        self.error_message = str(error_message)

        # Get the original exception traceback
        _, _, exc_tb = error_details.exc_info()

        if exc_tb is not None:
            self.line_no = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename
            self.function_name = exc_tb.tb_frame.f_code.co_name
        else:
            self.line_no = None
            self.file_name = None
            self.function_name = None

    def __str__(self):
        return (
            f"Error occurred in Python script "
            f"[{self.file_name}], "
            f"function [{self.function_name}], "
            f"line [{self.line_no}]: "
            f"{self.error_message}"
        )


# if __name__ == "__main__":
#     try:
#         logger.info("Entering the try block")

#         a = 1 / 0

#         print("This will not be printed:", a)

#     except Exception as e:
#         custom_exception = NetworkSecurityException(e, sys)
#         print(custom_exception)
#         raise custom_exception from e 