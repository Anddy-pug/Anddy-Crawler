import asyncio

async def say_hello():
    print("Hello!")
    await asyncio.sleep(2)  # Simulate a non-blocking I/O operation
    print("Finished waiting!")

async def say_goodbye():
    print("Goodbye!")
    await asyncio.sleep(1)  # Simulate a non-blocking I/O operation
    print("Finished waiting!")

async def main():
    # Create coroutine objects
    hello_coro = say_hello()  # Returns a coroutine object
    goodbye_coro = say_goodbye()  # Returns a coroutine object

    # Run both coroutines concurrently
    await asyncio.gather(hello_coro, goodbye_coro)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
