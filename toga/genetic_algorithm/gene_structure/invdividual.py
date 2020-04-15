import math

import yaml


class Metrics(object):
    MIN = float("-inf")
    MAX = float("inf")

    def __init__(self, fitness_metrics={}, maximize=True, metrics_df=None):
        # Optimization Strategy
        self.fitness_metrics = fitness_metrics

        self.fitness_metrics_keys = list(self.fitness_metrics.keys())

        self.maximize = maximize
        # Scores
        self.metrics_df = metrics_df

        self.score = {}

    def fill_invalid_values(self, key):
        _range = self.fitness_metrics[key].get('range')
        self.score[key] = max(_range)
        if self.maximize:
            self.score[key] = min(_range)

    def compose(self):
        # Set score to the worst possible value based on optimization strategy if metrics aren't found
        if self.metrics_df is None:
            for _ in self.fitness_metrics_keys:
                self.fill_invalid_values(_)
            return

        for _ in self.fitness_metrics_keys:
            self.score[_] = float(self.metrics_df[_].mean())
            value = self.score[_]
            if math.isinf(value) or math.isnan(value):
                self.fill_invalid_values(_)

        return self.score


class Lineage(object):

    def __init__(self, mutator='', parent1=None, parent2=None, generation_num=0):
        self.mutator = mutator
        self.parent1 = None if parent1 is None else parent1.get('uuid')
        self.parent2 = None if parent2 is None else parent2.get('uuid')
        self.generation_num = generation_num

    def compose(self):
        return {"mutator": self.mutator,
                "parent1": self.parent1,
                "parent2": self.parent2,
                "generation_num": self.generation_num
                }


class Genetics(object):

    def __init__(self, gene={}):
        self.gene = gene

    def compose(self):
        return {"gene": self.gene}


class Individual(object):
    def __init__(self,  uuid='',  metrics=Metrics(), genetics=Genetics(), lineage=Lineage()):
        self.uuid = uuid  # unique identifier
        self.metrics = metrics  # Performance
        self.genetics = genetics  # This individuals params
        self.lineage = lineage  # information about this individuals immediate lineage
        self.out_path = None

    def convert_to_dict(self):
        individual = {
            'path': self.out_path,
            'uuid': self.uuid,
            'metrics': self.compose_metrics(),
            'genetics': self.genetics.compose(),
            'lineage': self.lineage.compose()}
        return individual

    def compose_metrics(self):
        return self.metrics.compose()

    def serialize(self):
        with open(self.out_path, 'w') as outfile:
            print(self.convert_to_dict())
            yaml.dump(self.convert_to_dict(), outfile)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
