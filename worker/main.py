import time
import os
import boto3
import schedule
from dotenv import load_dotenv
from scraper import fetch_all
from botocore.exceptions import ClientError

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMO_TABLE = "TrendingData"

def get_dynamo_table():
    try:
        dynamodb = boto3.resource(
            "dynamodb", 
            region_name=AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        return dynamodb.Table(DYNAMO_TABLE)
    except Exception as e:
        print(f"AWS Init Error: {e}")
        return None

def run_job():
    print(f"\n--- Starting Job: {time.ctime()} ---")
    
    # 1. Fetch Data
    results = fetch_all()
    
    # 2. Push to DynamoDB
    table = get_dynamo_table()
    if not table:
        print("⚠️ DynamoDB resource not available. Check credentials.")
        return

    for res in results:
        if not res: continue
        
        try:
            # DynamoDB Item Structure
            # Partition Key: source (String)
            # Attributes: data (List/Map), updated_at (String)
            
            # Need to serialize float/decimals for DynamoDB or use a sterilizer.
            # Boto3 handles basic types well, but float->Decimal conversion is sometimes needed.
            # We'll rely on boto3's default behavior for now, but might need simplejson/decimal later.
            
            item = {
                "source": res['source'],
                "data": res['data'],
                "updated_at": str(time.time())
            }
            
            table.put_item(Item=item)
            print(f"✅ Pusheed {res['source']} to DynamoDB")
            
        except ClientError as e:
            print(f"❌ DynamoDB Write Error: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🚀 Trending Worker v2 (AWS Edition) Started")
    print(f"Targeting DynamoDB Table: {DYNAMO_TABLE}")
    
    # Start specific HTTP server for App Runner Health Checks
    import http.server
    import socketserver
    import threading

    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    
    def start_health_server():
        print(f"🏥 Health check server listening on port {PORT}")
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
            
    # Run server in background thread
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()

    # Run once
    run_job()
    
    # Schedule
    schedule.every(10).seconds.do(run_job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
