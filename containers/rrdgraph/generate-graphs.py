import os
import rrdtool
import time

RRD_FOLDER = "/app/rrd_files"
GRAPH_FOLDER = "/app/graphs"
os.makedirs(GRAPH_FOLDER, exist_ok=True)

def generate_graph(metric_name):
    rrd_file = os.path.join(RRD_FOLDER, f"{metric_name}.rrd")
    graph_file = os.path.join(GRAPH_FOLDER, f"{metric_name}.png")
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

# List all RRD files and generate graphs
for filename in os.listdir(RRD_FOLDER):
    if filename.endswith(".rrd"):
        metric = filename[:-4]
        generate_graph(metric)
