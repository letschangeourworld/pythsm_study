'''
공장에 작업장이 3개가 있고 각 작업장에 작업자가 1명씩 있다.
작업장 3개는 연속되어 있어서 이전 작업이 끝나면 다음 작업장으로
제품이 옮겨지게 되고 이 제품에 대한 작업을 각 작업장 안에 있는 
작업자가 일을 하여 다음 작업장으로 넘기어 준다. 
이런 생산공정을 salabim을 이용하여 시뮬레이션하는 코드를 작성해보자.
또한 animate()함수를 이용해 보자.
'''


import salabim as sim

class Factory:
    def __init__(self, num_workers=1, num_workshops=3):
        self.env = sim.Environment(trace=False)
        self.workers = [Worker(i + 1, self.env) for i in range(num_workers)]
        self.workshops = [Workshop(i + 1, self.env) for i in range(num_workshops)]
        self.jobs = [Job(self.workshops[0], self.env)]

    def simulate(self):
        self.env.animate(True)
        self.env.run()

class Worker(sim.Component):
    def process(self):
        while True:
            if len(self.workshop.queue) > 0:
                job = self.workshop.queue.pop(0)
                yield self.hold(job.process_time())
                if self.workshop.left is not None:
                    self.workshop.left.queue.append(job)
                else:
                    job.enter(self.factory.env.wait_for_exit)
            else:
                if self.workshop.left is not None:
                    self.workshop.left.worker.queue.append(self)
                yield self.passivate()

    def set_workshop(self, workshop):
        self.workshop = workshop

    def set_factory(self, factory):
        self.factory = factory

class Workshop:
    def __init__(self, id, env):
        self.id = id
        self.get_out_of = None
        self.left = None
        self.queue = []
        self.worker = Worker(env=env)
        self.worker.set_workshop(self)
        self.worker.set_factory(env.factory)
        self.worker.activate()

class Job(sim.Component):
    def __init__(self, workshop, env):
        self.workshop = workshop
        self.env = env
        self.set_exit(env.exit)

    def process_time(self):
        return self.env.uniform(10, 20)

    def enter(self, next):
        self.next = next
        if self.workshop.get_out_of is None:
            self.workshop.worker.queue.append(self)
        else:
            self.workshop.get_out_of.queue
