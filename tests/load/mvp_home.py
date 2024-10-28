# -*- coding: utf-8 -*-
from locust import HttpUser, between, task


class MVPTasks(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_square(self):
        self.client.get('/')
