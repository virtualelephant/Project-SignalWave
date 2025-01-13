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

    try:
        end_time = int(time.time())
        start_time = end_time - 86400  # Last 24 hours

        rrdtool.graph(
            graph_file,
            "--start", str(start_time),
            "--end", str(end_time),
            "--title", f"{metric_name} over the last 24 hours",
            "--vertical-label", "Value",
            f"DEF:mydata={rrd_file}:value:AVERAGE",
            "LINE1:mydata#0000FF:Value"
        )
        logger.info(f"Graph generated for metric: {metric_name}")
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
