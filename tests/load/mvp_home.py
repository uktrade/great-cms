# -*- coding: utf-8 -*-
from locust import HttpLocust, TaskSet, between, task


class MVPTasks(TaskSet):

    @task
    def home_page(self):
        self.client.get('/')


class MVP(HttpLocust):
    host = 'http://localhost:8020'
    task_set = MVPTasks
    wait_time = between(1, 2)
