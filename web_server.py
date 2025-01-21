import asyncio
import nest_asyncio
from aiohttp import web

# Apply nest_asyncio to support nested event loops (important for running multiple async tasks concurrently)
nest_asyncio.apply()

# Handler for the home route to confirm the web server is working
async def home(request):
    return web.Response(text="Telegram Bot is running on aiohttp server!")

# Initialize the web application and add routes
async def init_app():
    app = web.Application()
    app.router.add_get('/', home)  # The home route when accessing the root URL
    return app

# Start the web server on port 8080
async def start_web_server():
    # Initialize the web application
    app = await init_app()

    # Create a runner for the application
    runner = web.AppRunner(app)
    await runner.setup()

    # Create and start the TCP site bound to 0.0.0.0 and port 8080
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    print("Web server is starting on http://0.0.0.0:8080...")  # Log when the server is starting
    await site.start()

    print("Web server is running...")  # Log once the server is up

    # Keep the server running indefinitely
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour (this keeps the server running)

# Entry point to start the server if this file is executed directly
if __name__ == '__main__':
    try:
        print("Starting web server...")
        asyncio.run(start_web_server())  # Run the web server with asyncio
    except Exception as e:
        print(f"Error starting the web server: {e}")
