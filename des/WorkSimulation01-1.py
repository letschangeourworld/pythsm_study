import salabim as sim

class Workshop(sim.Component):
    def __init__(self, id, env, capacity):
        self.id = id
        self.env = env
        self.capacity = capacity
        self.queue = sim.Queue(name="queue%d" % id)
        
    def add_job(self, job):
        self.queue.append(job)

    def has_next_job(self):
        return len(self.queue) > 0

    def get_next_job(self):
        return self.queue.pop(0)

    def can_move(self):
        return len(self.next_worker) < self.capacity

    def process(self):
        while True:
            if self.has_next_job() and self.can_move():
                yield self.hold(0)
                job = self.get_next_job()
                next_workshop = workshops[self.id]
                next_workshop.add_job(job)
            else:
                yield self.passivate()

class Job(sim.Component):
    def __init__(self):
        self.set_exit(env.exit)

    def process_time(self):
        return 15

    def insert(self, workshop):
        workshop.add_job(self)

'''
다음은 Salabim 라이브러리를 사용하여 
공정 작업 시뮬레이션을 수행하는 예시 코드
'''

class Workshop(sim.Component):
    def __init__(self, id, env, capacity):
        self.id = id
        self.env = env
        self.capacity = capacity
        self.queue = sim.Queue(name="queue%d" % id)
        
    def add_job(self, job):
        self.queue.append(job)

    def has_next_job(self):
        return len(self.queue) > 0

    def get_next_job(self):
        return self.queue.pop(0)

    def can_move(self):
        return len(self.next_worker) < self.capacity

    def process(self):
        while True:
            if self.has_next_job() and self.can_move():
                yield self.hold(0)
                job = self.get_next_job()
                next_workshop = workshops[self.id]
                next_workshop.add_job(job)
            else:
                yield self.passivate()

class Job(sim.Component):
    def __init__(self):
        self.set_exit(env.exit)

    def process_time(self):
        return 15

    def insert(self, workshop):
        workshop.add_job(self)

env = sim.Environment()
workshops = {}
for i in range(4):
    workshops[i] = Workshop(i, env, 1)

for i in range(100):
    Job().insert(workshops[0])

env.run()


'''
이 코드는 4개의 Workshop 객체와 100개의 Job 객체를 생성한다.
`Workshop` 클래스는 공정 작업을 나타내며, 
각각의 작업장은 고유한 ID와 작업자 수용 인원(capacity), 
작업 대기열(queue)을 가지고 있습니다. 
`Job` 클래스는 생산할 제품을 나타내며, 
이 객체를 작업장에 추가하여 작업을 시작합니다.
`Job` 클래스의 `process_time` 메소드에서는 
제품을 일정 시간 동안 처리하는 시간을 설정합니다.
`Workshop` 클래스의 `process` 메소드에서는 
대기열에 작업이 있는지 확인한 후, 작업장에 작업
'''

class Workshop(sim.Component):
    def __init__(self, id, env, capacity):
        self.id = id
        self.env = env
        self.capacity = capacity
        self.queue = sim.Queue(name="queue%d" % id)

    def add_job(self, job):
        self.queue.append(job)

    def has_next_job(self):
        return len(self.queue) > 0

    def get_next_job(self):
        return self.queue.pop(0)

    def can_move(self):
        return len(self.next_worker) < self.capacity

    def process(self):
        while True:
            if self.has_next_job() and self.can_move():
                yield self.hold(0)
                job = self.get_next_job()
                if self.id == 3:
                    Output.insert(job)
                else:
                    next_workshop = workshops[self.id]
                    next_workshop.add_job(job)
            else:
                yield self.passivate()

class Job(sim.Component):
    def __init__(self):
        self.set_exit(env.exit)

    def process_time(self):
        return 15

    def insert(self, workshop):
        workshop.add_job(self)


class Factory(sim.Component):
    def process(self):
        while True:
            yield self.hold(0)
            if JobGenerator.can_generate_job():
                JobGenerator.generate_job()
                job = Job()
                workshops[0].add_job(job)

            yield self.hold(1)

def animate(env):
    while True:
        yield env.timeout(0.1)
        env.set_animate(False)
        g.settext(
            "Queue 1 : {}\nQueue 2 : {}\nQueue 3 : {}".format(
                len(workshops[0].queue), len(workshops[1].queue), len(workshops[2].queue)
            )
        )

        for i, workshop in enumerate(workshops.values()):
            for j, worker in enumerate(workshop.next_worker):
                w[i]


'''
다음은 공장에 작업장이 3개가 있고 
각 작업장에 작업자가 1명씩 있는 
상황에서 Salabim 라이브러리를 사용하여 
작업장 간 이동이 가능한 생산 공정을 
시뮬레이션하는 코드입니다.
animate를 통해 시뮬레이션 결과를 보여줍니다.
'''

