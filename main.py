import platform
import psutil
import cpuinfo
import time
import jinja2
import socket
import webbrowser


def render_template(template_path, data):
    """Renders the given template with the given data."""

    template = jinja2.Template(open(template_path).read())
    return template.render(data)


def collect_system_info():
    """Collects system information."""
    uname = platform.uname()._asdict()
    system_info = {}
    system_info["OS"] = uname["system"]
    system_info["Architecture"] = uname["machine"]
    system_info["CPU"] = f"{cpuinfo.get_cpu_info()['brand_raw']} ({psutil.cpu_count()} cores)"
    system_info["Memory"] = f"{round(psutil.virtual_memory().total / (1024.0 ** 3))} GB"

    # Additional Information
    system_info["CPU Usage"] = f"{psutil.cpu_percent(interval=1)}%"
    system_info["Memory Usage"] = f"{psutil.virtual_memory().percent}%"
    disk_partitions = psutil.disk_partitions()
    disk_info = []
    for partition in disk_partitions:
        partition_usage = psutil.disk_usage(partition.mountpoint)
        disk_info.append({
            "Mount Point": partition.mountpoint,
            "Total Disk Space": f"{round(partition_usage.total / (1024.0 ** 3))} GB",
            "Used Disk Space": f"{round(partition_usage.used / (1024.0 ** 3))} GB",
            "Free Disk Space": f"{round(partition_usage.free / (1024.0 ** 3))} GB",
            "Disk Usage": f"{partition_usage.percent}%"
        })

    # Top Processes
    top_cpu_processes = [proc.info for proc in psutil.process_iter(
        attrs=['name', 'pid', 'cpu_percent'])]
    top_cpu_processes = sorted(
        top_cpu_processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]

    top_memory_processes = [proc.info for proc in psutil.process_iter(
        attrs=['name', 'pid', 'memory_percent'])]
    top_memory_processes = sorted(
        top_memory_processes, key=lambda x: x['memory_percent'], reverse=True)[:5]

    # User Information
    users = psutil.users()
    user_info = [{"User": user.name, "Terminal": user.terminal, "Login Time": time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(user.started))} for user in users]

    # Network Information
    network_info = psutil.net_if_addrs()
    network_data = {}
    for interface, addrs in network_info.items():
        network_data[interface] = [
            addr.address for addr in addrs if addr.family == socket.AF_INET]

    return [system_info, disk_info, user_info, network_data, top_cpu_processes, top_memory_processes]


if __name__ == "__main__":
    [system_info, disk_info, user_info, network_data, top_cpu_processes,
     top_memory_processes] = collect_system_info()

    report_html = render_template("template.html", {
        "report_date": time.strftime('%Y-%m-%d %H:%M:%S'),
        "system_info": system_info,
        "disk_info": disk_info,
        "user_info": user_info,
        "network_data": network_data,
        "top_cpu_processes": top_cpu_processes,
        "top_memory_processes": top_memory_processes,
    })

    with open("report.html", "w") as f:
        f.write(report_html)

    webbrowser.open("report.html")
