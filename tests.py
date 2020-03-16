from function_logger import log_function
import time


@log_function
def sum_five_seconds(x, y):
    # Function text output
    print(x)
    print(y)

    # Total execution time
    time.sleep(5)

    # Value returned by function
    return x + y


if __name__ == '__main__':
    sum_five_seconds(9, 7)
