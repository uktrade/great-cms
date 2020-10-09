# -*- coding: utf-8 -*-
from locust import HttpUser, TaskSet, between, task


class MVPTasks(TaskSet):
    @task
    def home_page(self):
        self.client.get('/')


class MVP(HttpUser):
    host = 'http://localhost:8020'
    tasks = [MVPTasks]
    wait_time = between(1, 2)
