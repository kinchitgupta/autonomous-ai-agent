# agent/memory.py

memory = {
    "last_task": None,
    "last_result": None
}

def update_memory(task, result):
    memory["last_task"] = task
    memory["last_result"] = result

def get_memory():
    return memory
