'''
그런데 여기에서 각 작업자들의 이름은 PSJ, SGJ, YCH이다. 
그리고 작업장 이름은 A, B, C 이다. 
A작업장에는 PSJ가 작업을 하고,
B작업장에는 SGJ이 작업을 하고,
C작업장에는 YCH가 작업을 한다. 
A작업장의 PSJ의 작업이 끝난 후에 B작업장의 SGJ이 작업을 하고
B작업장의 SGJ의 작업이 끝나면 C작업장의 YCH가 작업을 하게 된다.
그러나 SGJ이 작업이 끝나지 않았다면 A작업장에서 제품이 B로 투입되어서는 안 된다. 
또한 YCH의 작업이 끝나지 않았다면 제품이 B에서 C작업장으로 투입되어서는 안 된다.
PSJ의 작업시간은 제품 1개당 45초이고,
SGJ의 작업시간은 제품 1개당 30초이고,
YCH의 작업시간은 제품 1개당 55초이다.
제품은 총 5000개를 생산완료시키려면 총 걸리는 시간은 얼마인지 
salabim을 이용하여 시뮬레이션하는 코드를 만들어 보자.
또 눈으로 공정과정을 이해할 수 있게 3D로 표현하는 코드도 포함해 보자.
'''

import salabim as sim

class A_Worker(sim.Component):
    def process(self):
        while True:
            if A_Workshop.can_move():
                yield self.hold(0)
                job = A_Workshop.get_next_job()
                
                yield self.hold(job.process_time())
                B_Workshop.insert_job(job)
            else:
                yield self.passivate()

class B_Worker(sim.Component):
    def process(self):
        while True:
            if B_Workshop.in_queue(self) and not C_Workshop.is_busy():
                yield self.hold(0)
                job = B_Workshop.get_next_job(self)
                yield self.hold(job.process_time())
                C_Workshop.insert_job(job)
            else:
                yield self.passivate()

class C_Worker(sim.Component):
    def process(self):
        while True:
            if C_Workshop.in_queue(self):
                yield self.hold(0)
                job = C_Workshop.get_next_job(self)
                yield self.hold(job.process_time())
                C_Workshop.remove_job(job)
            else:
                yield self.passivate()

class Job(sim.Component):
    def __init__(self):
        self.set_exit(env.exit)

    def process_time(self):
        if self.current_workshop.id == 1:
            return 45
        elif self.current_workshop.id == 2:
            return 30
        elif self.current_workshop.id == 3:
            return 55

    def insert(self, workshop):
        workshop.add_job(self)

class Workshop:
    def __init__(self, id, env):
        self.id = id
        self.env = env
        self.worker = None
        self.current_job = None
        self.waiting_jobs = []
        self.next_workshop = None

    def add_job(self, job):
        self.waiting_jobs.append(job)

    def get_next_job(self, worker):
        self.worker = worker
        self.current_job = self.waiting_jobs.pop(0)
        self.current_job.current_workshop = self
        return self.current_job
