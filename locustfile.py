from locust import HttpUser, task, between
import random

QUERIES = [
    "What is a linked list?",
    "Explain stacks",
    "What is recursion?",
    "Define queue",
    "Explain binary tree",
]

class FlashRAGUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def chat_query(self):
        payload = {
            "query": random.choice(QUERIES)
        }

        with self.client.post(
            "/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:

            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Failed with status {response.status_code}"
                )

    @task(1)
    def health_check(self):
        self.client.get("/api/health")