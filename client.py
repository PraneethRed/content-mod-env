import requests


class ContentModClient:
    def __init__(self, base_url="http://localhost:7860"):
        self.base_url = base_url

    def reset(self, task_id=None):
        payload = {"task_id": task_id} if task_id else {}
        r = requests.post(f"{self.base_url}/reset", json=payload)
        return r.json()

    def step(self, action, task_id=None):
        payload = {"action": action}
        if task_id:
            payload["task_id"] = task_id
        r = requests.post(f"{self.base_url}/step", json=payload)
        return r.json()

    def state(self, task_id=None):
        params = {"task_id": task_id} if task_id else {}
        r = requests.get(f"{self.base_url}/state", params=params)
        return r.json()
