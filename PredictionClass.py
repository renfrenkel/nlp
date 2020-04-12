class PreditcionClass:

    def __init__(self, className):
        self.name = className
        self.bagOfWords = {}
        self.AddOnProbability = {}
        self.vocabSize = 0
        self.unknownProbability = 0
        self.priorProbability = 0
