class Metric(object):

    def __init__(self, name, fixed_axis, axis_range, partitions, index):
        self.name = name
        self.fixed_axis = fixed_axis
        self.axis_range = axis_range
        self.partitions = partitions
        self.index = index


class Metrics(object):

    def __init__(self, input_dictionary):
        self.input_dictionary = input_dictionary
        self.metrics = self.get_metrics()

    def get_metrics(self):
        metrics = []
        for key, value in self.input_dictionary.items():
            metrics.append(Metric(name=key,
                                  fixed_axis=value.get('fixed_axis'),
                                  axis_range=value.get('range'),
                                  partitions=value.get('partitions'),
                                  index=value.get('index')))
        # sort by index value
        metrics = sorted(metrics, key=lambda x: x.index)
        return metrics


if __name__ == '__main__':
    import doctest
    doctest.testmod()
