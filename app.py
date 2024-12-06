from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils import fetch_and_store_earthquake_data

# Create Flask app instance
app = create_app()

def run_batch_process():
    """Fetch earthquake data and store it in MongoDB."""
    try:
        print("Running batch process to fetch earthquake data...")
        fetch_and_store_earthquake_data()
        print("Batch process completed successfully!")
    except Exception as e:
        print(f"Batch process failed: {e}")

if __name__ == '__main__':
    # Initialize the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_batch_process, 'interval', hours=24)  # Schedule to run every 24 hours
    scheduler.start()

    # Run Flask app
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()  # Shut down the scheduler gracefully
