
'''
그런데 여기에서 제품이 작업장 간에 이동하는데 이동 시간이 있어. 
이전 작업장에서 다음 작업장으로 제품이 움직일 때, 
경로가 2개가 있어서 둘 중의 1개의 경로를 선택하여 제품이 이동된다.
2개의 경로는 모두 제품이 10개씩 한 줄로 줄을 설 수 있게 해 놓았고,
두 경로 중에 비어있는 경로로 제품이 투입될 수가 있고,
두 경로가 모두 차 있으면 작업장 내에서 대기해야 한다.
또한 두 경로에 제품 한 개 이상 대기하고 있으면 이후의 작업장의 작업자가 쉬는 일은 없게 된다. 
두 경로가 모두 비어있으면, 이전 작업장에서 제품이 둘 중의 어떤 경로를 이용하든 관계가 없다.
두 경로의 길이는 30미터이고 생산라인 속도는 초속 2미터이다. 
그러니까 두 경로가 비어있을 때, 제품이 한 경로를 통해 이동하는데 필요한 시간은 15초가 되는 것이다.
이런 조건을 포함하여 작성한 코드를 다시 작성해 보자.
'''

import salabim as sim

class A_Worker(sim.Component):
    def process(self):
        while True:
            if A_Workshop.has_next_job() and A_Workshop.can_move():
                yield self.hold(0)
                job = A_Workshop.get_next_job()
                
                yield self.hold(job.process_time())
                B_Workshop.insert_job(job)
            else:
                yield self.passivate()

class B_Worker(sim.Component):
    def process(self):
        while True:
            if B_Workshop.has_next_job(self) and B_Workshop.can_move():
                yield self.hold(0)
                job = B_Workshop.get_next_job(self)
                yield self.hold(job.process_time())
                C_Workshop.insert_job(job)
            else:
                yield self.passivate()

class C_Worker(sim.Component):
    def process(self):
        while True:
            if C_Workshop.has_next_job(self):
                yield self.hold(0)
                job = C_Workshop.get_next_job(self)
                yield self.hold(job.process_time())
                C_Workshop.remove_job(job)
                Output.insert_job(job)
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
        if workshop.id in [1, 2]:
            queue = workshop.queue_A if len(workshop.queue_A) < len(workshop.queue_B) else workshop.queue_B
            queue.append(self)
            if len(queue) == 10:
                workshop.full_queues.append(queue)

class Workshop:
    def __init__(self, id, env, length):
        self.id = id
        self.env = env
        self.length = length
        self.worker = None
        self.current_job = None
        self.waiting_jobs = []
        self.next_workshop = None
        self.queue_A = []
        self.queue_B =

'''
두 경로 중에 한 개의 경로를 이용하는 제품의 수가 10개이면 
가득 차 있는 것으로 간주한다.
제품이 한 경로 이용하여 다음 작업장까지 가는 데 걸리는 소요시간은 15초이다. 
이것을 포함하는 코드로 다시 작성해 본다.
'''

import salabim as sim

class A_Worker(sim.Component):
    def process(self):
        while True:
            if A_Workshop.has_next_job() and A_Workshop.can_move():
                yield self.hold(0)
                job = A_Workshop.get_next_job()
                
                yield self.hold(15)
                B_Workshop.insert_job(job)
            else:
                yield self.passivate()

class B_Worker(sim.Component):
    def process(self):
        while True:
            if B_Workshop.has_next_job(self) and B_Workshop.can_move():
                yield self.hold(0)
                job = B_Workshop.get_next_job(self)
                yield self.hold(15)
                C_Workshop.insert_job(job)
            else:
                yield self.passivate()

class C_Worker(sim.Component):
    def process(self):
        while True:
            if C_Workshop.has_next_job(self):
                yield self.hold(0)
                job = C_Workshop.get_next_job(self)
                yield self.hold(15)
                C_Workshop.remove_job(job)
                Output.insert_job(job)
            else:
                yield self.passivate()

class Job(sim.Component):
    def __init__(self):
        self.set_exit(env.exit)

    def process_time(self):
        return 45 if self.current_workshop.id == 1 else 30 if self.current_workshop.id == 2 else 55

    def insert(self, workshop):
        workshop.add_job(self)

Workshop(1, env, 3)
Workshop(2, env, 2)
Workshop(3, env, 4)

env.run(till=1000)

'''
`till=1000`은 Salabim 시뮬레이션의 최대 시간을 1000으로 설정하는 것이다.
`env.run(till=1000)` 코드가 실행되면,
시뮬레이션이 0에서 1000까지 진행된다. 
이 시간동안 발생하는 이벤트들이 처리되고, 
시뮬레이션의 결과가 출력된다.
따라서 `till=1000`은 시뮬레이션의 진행 시간 제한을 설정하는 것이다.
'''
