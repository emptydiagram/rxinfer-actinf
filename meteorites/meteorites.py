from operator import itemgetter
import random
import time
import turtle

def set_seed(seed):
    random.seed(seed)


class MeteoritesEnv:
    def __init__(self, config):
        ax, ay, dt, observable_region_sizes, observation_sigma, meteorites_config \
            = itemgetter('ax', 'ay', 'dt', 'observable_region_sizes', 'observation_sigma', 'meteorites')(config)
        self.ax = ax
        self.ay = ay
        self.dt = dt
        self.observation_sigma = observation_sigma

        r_w, r_h = observable_region_sizes
        llx, urx, lly, ury = (-r_w / 2, r_w / 2, 0, r_h)
        self.observable_region = (llx, lly, urx, ury)

        self.meteorites = { met['id'] : { 'px': met['px'], 'py': met['py'], 'p0x': met['px'], 'p0y': met['py'], 'v0x': met['vx'], 'v0y': met['vy'] }
            for met in meteorites_config }
        self.t = 0

    def meteorite_is_observable(self, mid):
        return self.meteorite_in_range(mid, self.observable_region)

    def meteorite_in_range(self, mid, window):
        llx, lly, urx, ury = window
        m = self.meteorites[mid]
        return llx <= m['px'] and m['px'] <= urx and lly <= m['py'] and m['py'] <= ury

    def step(self, obs_window=None):
        # x(t) = x(0) + v(0) t + a t^2 / 2
        self.t += self.dt
        observable_mets = []
        observed_mets = []
        for mid, m in self.meteorites.items():
            m['px'] = m['p0x'] + m['v0x'] * self.t + self.ax * self.t**2 / 2
            m['py'] = m['p0y'] + m['v0y'] * self.t + self.ay * self.t**2 / 2
            if self.meteorite_is_observable(mid):
                observable_mets.append([mid, m['px'], m['py']])

            # for now, observe entire region. TODO: restrict to window
            if self.meteorite_is_observable(mid):
                noise_x = random.gauss(mu=0.0, sigma=self.observation_sigma)
                noise_y = random.gauss(mu=0.0, sigma=self.observation_sigma)
                observed_mets.append([mid, m['px'] + noise_x, m['py'] + noise_y])
        return observable_mets, observed_mets


class EnvDisplay:
    def __init__(self, observable_region_sizes, width=800):
        r_w, r_h = observable_region_sizes
        llx, urx, lly, ury = (-r_w / 2, r_w / 2, 0, r_h)
        W_H_ratio = r_w / r_h
        W = width
        H = W / W_H_ratio

        self.screen = turtle.Screen()
        self.screen.setup(width=W, height=H)
        self.screen.setworldcoordinates(llx, lly, urx, ury)
        self.screen.tracer(0)

        self.met_size = 0.4

        self.met_turtles = {}
        self.obs_turtles = {}

    def step(self, dt, observable_mets, observed_mets):
        for mt in self.met_turtles.values():
            mt.clear()
            mt.hideturtle()

        for ot in self.obs_turtles.values():
            ot.clear()
            ot.hideturtle()

        for (mid, mx, my) in observable_mets:
            if mid not in self.met_turtles.keys():
                tur = turtle.Turtle()
                tur.hideturtle()
                tur.shape("circle")
                tur.color("#333333")
                tur.shapesize(self.met_size, self.met_size)
                tur.penup()
                self.met_turtles[mid] = tur
            self.met_turtles[mid].setposition(mx, my)
            self.met_turtles[mid].showturtle()

        for (mid, mx, my) in observed_mets:
            if mid not in self.obs_turtles.keys():
                tur = turtle.Turtle()
                tur.hideturtle()
                tur.shape("circle")
                tur.color("#0000ff")
                tur.fillcolor("")
                tur.shapesize(self.met_size, self.met_size)
                tur.penup()
                self.obs_turtles[mid] = tur
            self.obs_turtles[mid].setposition(mx, my)
            self.obs_turtles[mid].showturtle()


        self.screen.update()
        time.sleep(dt)



def run(config):
    env = MeteoritesEnv(config)
    display = EnvDisplay(config['observable_region_sizes'])

    while True:
        observable_mets, observed_mets = env.step()
        display.step(config['dt'], observable_mets, observed_mets)


if __name__ == '__main__':
    seed = 628318
    set_seed(seed)

    config = {
        'ax': 0.005,
        'ay': -0.02,
        'dt': 0.1,
        'observable_region_sizes': (10, 10),
        'observation_sigma': 0.1,
        'meteorites': [
            {
                'id': 1,
                'px': 0.0,
                'py': 5.0,
                'vx': 0.01,
                'vy': -0.03,
            },
            {
                'id': 2,
                'px': -4.5,
                'py': 9.5,
                'vx': -0.01,
                'vy': -0.02,
            },
            {
                'id': 3,
                'px': 10.5,
                'py': 7.5,
                'vx': -0.5,
                'vy': -0.02,
            },
            {
                'id': 4,
                'px': -4.5,
                'py': 2.5,
                'vx': 0.01,
                'vy': 0.1,
            },
        ]
    }

    run(config)
