class MetricsCalculator:
    def __init__(self):
        pass
    def calculate_rating_avarage(self, data):
        # TODO: add preprocessing filtering for data, but not in MetricsCalculator
        avarage = data['rating'].mean()
        return avarage

    def calculate_rating_distribution(self, data):
        distribution = data['rating'].value_counts(normalize=True)
        return distribution