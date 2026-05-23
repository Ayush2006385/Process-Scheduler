import tkinter as tk
from tkinter import ttk

window = tk.Tk()
window.title("CPU Scheduler")
window.geometry("800x900")


label_algo = tk.Label(window, text="Select Algorithm")
label_algo.pack(pady=5)

algo_var = tk.StringVar()
dropdown = ttk.Combobox(window, textvariable=algo_var)
dropdown["values"] = [ "First Come First Serve (FCFS)", "Preemptive Shortest Job First (SRTF)", "Round Robin", "Non Preemptive Priority Scheduling"]
dropdown.current(0)
dropdown.pack(pady=5)


quantum_label = tk.Label(window, text="Time Quantum (RR only):")
quantum_entry = tk.Entry(window, width=6)


def toggle_pr_column():
    for (pid, at, bt, pr) in rows:
        if "Priority" in algo_var.get():
            pr.grid()
        else:
            pr.grid_remove()



def on_algo_change(event):
    if "Round Robin" in algo_var.get():
        quantum_label.pack(pady=2)
        quantum_entry.pack(pady=2)
    else:
        quantum_label.pack_forget()
        quantum_entry.pack_forget()
    toggle_pr_column()

dropdown.bind("<<ComboboxSelected>>", on_algo_change)


def toggle_at():
    for (pid, at, bt, pr) in rows:
        if at_var.get():
            at.grid_remove()
        else:
            at.grid()

at_var = tk.BooleanVar()
checkbox = tk.Checkbutton(window, text="All processes arrive at time 0", variable=at_var, command=toggle_at)
checkbox.pack(pady=5)


rows = []

def add_row():
    row_frame = tk.Frame(window)
    row_frame.pack(pady=2)

    tk.Label(row_frame, text="PID:").grid(row=0, column=0)
    pid = tk.Entry(row_frame, width=6)
    pid.grid(row=0, column=1)

    tk.Label(row_frame, text="AT:").grid(row=0, column=2)
    at = tk.Entry(row_frame, width=6)
    at.grid(row=0, column=3)

    tk.Label(row_frame, text="BT:").grid(row=0, column=4)
    bt = tk.Entry(row_frame, width=6)
    bt.grid(row=0, column=5)

    tk.Label(row_frame, text="PR:").grid(row=0, column=6)
    pr_label = tk.Label(row_frame, text="PR:")
    pr_label.grid(row=0, column=6)
    pr = tk.Entry(row_frame, width=6)
    pr.grid(row=0, column=7)
    if "Priority" not in algo_var.get():
        pr_label.grid_remove()
        pr.grid_remove()
    rows.append((pid, at, bt, pr))

    if at_var.get():
        at.grid_remove()

    def delete_row():
        row_frame.destroy()
        rows.remove((pid, at, bt, pr))

    tk.Button(row_frame, text="✕", command=delete_row).grid(row=0, column=8)

btn_add = tk.Button(window, text="Add Process +", command=add_row)
btn_add.pack(pady=5)


canvas = tk.Canvas(window, width=700, height=100, bg="white")
canvas.pack(pady=10)


output_frame = tk.Frame(window)
output_frame.pack(pady=10)


def show_table(results):
    for widget in output_frame.winfo_children():
        widget.destroy()

    headers = ["PID", "AT", "BT", "Finish", "TAT", "WT"]
    for col, h in enumerate(headers):
        tk.Label(output_frame, text=h, borderwidth=1, relief="solid", width=8).grid(row=0, column=col)

    for row, p in enumerate(results):
        values = [p["pid"], p["at"], p["bt"], p["ct"], p["tat"], p["wt"]]
        for col, val in enumerate(values):
            tk.Label(output_frame, text=val, borderwidth=1, relief="solid", width=8).grid(row=row+1, column=col)


def draw_gantt(timeline):
    canvas.delete("all")

    total_time = timeline[-1]["ct"]
    scale = 600 / total_time
    x_start = 50
    y_top = 20
    y_bottom = 60

    colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
              "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac"]

    pid_colors = {}
    color_index = 0

    for p in timeline:
        if p["pid"] not in pid_colors:
            pid_colors[p["pid"]] = colors[color_index % len(colors)]
            color_index += 1

        x1 = x_start + p["start"] * scale
        x2 = x_start + p["ct"] * scale

        canvas.create_rectangle(x1, y_top, x2, y_bottom, fill=pid_colors[p["pid"]])
        canvas.create_text((x1 + x2) / 2, (y_top + y_bottom) / 2, text=p["pid"])
        canvas.create_text(x1, y_bottom + 15, text=str(int(p["start"])))

    last = timeline[-1]
    canvas.create_text(x_start + last["ct"] * scale, y_bottom + 15, text=str(last["ct"]))


def fcfs(process_list):
    process = sorted(process_list, key=lambda x: x["at"])
    ctime = 0
    result = []
    timeline = []

    for i in process:
        start = max(ctime, i["at"])
        finish = start + i["bt"]
        tat = finish - i["at"]
        wt = tat - i["bt"]
        ctime = finish

        result.append({"pid": i["pid"], "at": i["at"], "bt": i["bt"], "start": start, "ct": finish, "tat": tat, "wt": wt})
        timeline.append({"pid": i["pid"], "start": start, "ct": finish})

    return result, timeline


def srtf(process_list):
    ctime = 0
    remaining = {}
    for p in process_list:
        remaining[p["pid"]] = p["bt"]

    c = 0
    n = len(process_list)
    result = []
    timeline = []
    prev_pid = None

    while c != n:
        found = None
        min_rem = 9999

        for p in process_list:
            if p["at"] <= ctime and remaining[p["pid"]] > 0 and remaining[p["pid"]] < min_rem:
                found = p
                min_rem = remaining[p["pid"]]

        if found is None:
            ctime += 1
            continue

        if found["pid"] != prev_pid:
            if prev_pid is not None:
                timeline[-1]["ct"] = ctime
            timeline.append({"pid": found["pid"], "start": ctime})
            prev_pid = found["pid"]

        remaining[found["pid"]] -= 1
        ctime += 1

        if remaining[found["pid"]] == 0:
            found["ct"] = ctime
            found["tt"] = found["ct"] - found["at"]
            found["wt"] = found["tt"] - found["bt"]
            c += 1
            result.append({"pid": found["pid"], "at": found["at"], "bt": found["bt"],
                           "start": found["ct"] - found["bt"], "ct": found["ct"],
                           "tat": found["tt"], "wt": found["wt"]})

    if timeline:
        timeline[-1]["ct"] = ctime

    return result, timeline


def round_robin(process_list, quantum):
    processes = sorted(process_list, key=lambda x: x["at"])
    remaining = {p["pid"]: p["bt"] for p in processes}
    ctime = 0
    queue = []
    result = []
    timeline = []
    visited = set()
    done = set()

    while len(done) != len(processes):
        for p in processes:
            if p["at"] <= ctime and p["pid"] not in visited and p["pid"] not in done:
                queue.append(p)
                visited.add(p["pid"])

        if not queue:
            ctime += 1
            continue

        current = queue.pop(0)
        run_time = min(quantum, remaining[current["pid"]])
        start = ctime

        timeline.append({"pid": current["pid"], "start": start, "ct": start + run_time})

        remaining[current["pid"]] -= run_time
        ctime += run_time

        for p in processes:
            if p["at"] <= ctime and p["pid"] not in visited and p["pid"] not in done:
                queue.append(p)
                visited.add(p["pid"])

        if remaining[current["pid"]] == 0:
            done.add(current["pid"])
            tat = ctime - current["at"]
            wt = tat - current["bt"]
            result.append({"pid": current["pid"], "at": current["at"], "bt": current["bt"],
                           "ct": ctime, "tat": tat, "wt": wt})
        else:
            queue.append(current)

    return result, timeline


def priority_np(process_list):
    processes = sorted(process_list, key=lambda x: x["at"])
    remaining = list(processes)
    ctime = 0
    result = []
    timeline = []

    while remaining:
        available = [p for p in remaining if p["at"] <= ctime]

        if not available:
            ctime += 1
            continue

        current = min(available, key=lambda x: x["pr"])
        remaining.remove(current)

        start = max(ctime, current["at"])
        finish = start + current["bt"]
        tat = finish - current["at"]
        wt = tat - current["bt"]
        ctime = finish

        result.append({"pid": current["pid"], "at": current["at"], "bt": current["bt"],
                       "ct": finish, "tat": tat, "wt": wt})
        timeline.append({"pid": current["pid"], "start": start, "ct": finish})

    return result, timeline


def run_scheduler():
    process_list = []

    for (pid, at, bt, pr) in rows:
        pid_val = pid.get()
        bt_val = bt.get()

        if pid_val == "" or bt_val == "":
            continue

        bt_int = int(bt_val)
        pr_val = int(pr.get()) if pr.get() != "" else 0

        if at_var.get():
            at_int = 0
        else:
            at_int = int(at.get())

        process_list.append({"pid": pid_val, "at": at_int, "bt": bt_int, "pr": pr_val})

    alg = algo_var.get()

    if "FCFS" in alg:
        results, timeline = fcfs(process_list)
        show_table(results)
        draw_gantt(timeline)

    elif "SRTF" in alg:
        results, timeline = srtf(process_list)
        show_table(results)
        draw_gantt(timeline)

    elif "Round Robin" in alg:
        quantum = int(quantum_entry.get())
        results, timeline = round_robin(process_list, quantum)
        show_table(results)
        draw_gantt(timeline)

    elif "Priority" in alg:
        results, timeline = priority_np(process_list)
        show_table(results)
        draw_gantt(timeline)

btn_run = tk.Button(window, text="Run Scheduler", command=run_scheduler)
btn_run.pack(pady=10)

window.mainloop()
