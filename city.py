class City:
    def __init__(self, id, initial_resources, population, production_rates, utilization_exponents, growth_rate, x, y, nation, color):
        self.id = id
        self.resources = initial_resources  # list of resources
        self.population = population
        self.production_rates = production_rates  # list of production rates
        self.utilization_exponents = utilization_exponents  # list of utilization exponents
        self.growth_rate = growth_rate  # growth rate
        self.x = x
        self.y = y
        self.nation = nation
        self.color = color

    def produce_resources(self):
        # Add resources according to the city's production rates
        self.resources = [resource + rate for resource, rate in zip(self.resources, self.production_rates)]

    def project_utilization(self):
        # Project the resource utilization for the next round
        return [self.population ** exponent for exponent in self.utilization_exponents]

    def step(self):
        # Produce resources each round
        self.produce_resources()

        # Project the resource utilization for the next round
        projected_utilization = self.project_utilization()

        # Adjust the population based on the projected resource utilization
        for i, utilization in enumerate(projected_utilization):
            if utilization > self.resources[i]:
                self.population = int(self.resources[i] ** (1 / self.utilization_exponents[i]))
            elif self.resources[i] > 2 * utilization:
                self.population = int(self.population * (1 + self.growth_rate))

        # Utilize resources scaled by the adjusted population
        self.resources = [resource - self.population ** exponent for resource, exponent in zip(self.resources, self.utilization_exponents)]
