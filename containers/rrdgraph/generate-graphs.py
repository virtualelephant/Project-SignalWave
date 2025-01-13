import os
import rrdtool
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("generate-graphs")

# Directories for RRD files and generated graphs
RRD_FOLDER = "/app/rrd_files"
GRAPH_FOLDER = "/app/rrd_files"
os.makedirs(GRAPH_FOLDER, exist_ok=True)

def generate_graph(metric_name):
    """Generates a graph for a given metric."""
    rrd_file = os.path.join(RRD_FOLDER, f"{metric_name}.rrd")
    graph_file = os.path.join(GRAPH_FOLDER, f"{metric_name}.png")

    # Define units for metrics
    metric_units = {
        "dns_resolution_time": "seconds",
        "http_latency": "seconds",
        "http_response_code": "count",
        "request_size": "bytes",
        "response_size": "bytes",
        "packet_loss": "percentage",
        "jitter": "seconds",
    }

    unit = metric_units.get(metric_name, "Value")

    try:
        end_time = int(time.time())
        start_time = end_time - 86400  # Last 24 hours

        rrdtool.graph(
            graph_file,
            "--start", str(start_time),
            "--end", str(end_time),
            "--width", "1024",
            "--title", f"{metric_name} over the last 24 hours",
            "--vertical-label", unit,
            f"DEF:mydata={rrd_file}:value:AVERAGE",
            "AREA:mydata#00FF00:Value"
        )
        logger.info(f"Graph generated for metric: {metric_name} with unit {unit}")
    except Exception as e:
        logger.error(f"Error generating graph for {metric_name}: {e}")

def main():
    """Main loop for generating graphs."""
    while True:
        if not os.path.exists(RRD_FOLDER):
            logger.error(f"RRD folder {RRD_FOLDER} does not exist.")
            time.sleep(60)
            continue

        for filename in os.listdir(RRD_FOLDER):
            if filename.endswith(".rrd"):
                metric_name = filename[:-4]  # Remove .rrd extension
                generate_graph(metric_name)

        logger.info("Sleeping for 180 seconds before the next update.")
        time.sleep(180)

if __name__ == "__main__":
    main()
