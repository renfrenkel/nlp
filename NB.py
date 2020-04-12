from decimal import *
from math import log
from PredictionClass import PreditcionClass
import sys

# Make a bag of words for all classes
def fillBag(file, class1, class2):
    with open(file, "r") as parameterFile:
        for line in parameterFile:
            if line.startswith(class1.name):
                addWordsToBag(class1, line)
            if line.startswith(class2.name):
                addWordsToBag(class2, line)
            if line.startswith("Prior-Probabilities"):
                setPriorProbabilities(line, class1, class2)
            if line.startswith("Vocabulary"):
                setVocabSize(line, class1, class2)

# Set the size of the vocabulary 
def setVocabSize(vocabLine, class1, class2):
    words = vocabLine.split()
    words.pop()
    size = len(words)
    class1.vocabSize = size
    class2.vocabSize = size

# Set the prior probabilities
def setPriorProbabilities(line, class1, class2):
    splitLine = line.split(":")
    prior1 = (splitLine[1].split()[0].strip())
    prior2 = (splitLine[2].strip())
    class1.priorProbability = Decimal(prior1)
    class2.priorProbability = Decimal(prior2)

# Add words to dictionaries with the appropriate values 
def addWordsToBag(predictionClass, line):
    line = line.strip()
    words = line.split (" ")
    words.pop(0)
    for word in words:
        colonIndex = word.find(":")
        key = word[:colonIndex]
        value = int(word[colonIndex+1:len(word)])
        if key not in predictionClass.bagOfWords:
            predictionClass.bagOfWords[key] = value
        else:
            predictionClass.bagOfWords[key] += value

# Find the probability of each word in the bag of words
def findProbabilities(predictionClass, smoothingNumber):
    classWordCount = sum(predictionClass.bagOfWords.values())
    for word in predictionClass.bagOfWords:
        wordCount = predictionClass.bagOfWords[word]
        probability = (wordCount+Decimal(smoothingNumber))/(classWordCount+predictionClass.vocabSize)
        predictionClass.AddOnProbability[word] = probability
    unknownProbability = 1/(classWordCount+predictionClass.vocabSize)
    predictionClass.unknownProbability = Decimal(unknownProbability)

# Go through the test files and make class predictions
def calculatePredictions(testFile, class1, class2, outputFile, weighDeterminers):
    predictionCount = 0
    accurateCount = 0
    with open(testFile, "r") as testParameterFile:
        with open(outputFile, "a") as predictionOutputFile:
            for line in testParameterFile:
                class1Prediction = getPrediction(line, class1, weighDeterminers)
                class2Prediction = getPrediction(line, class2, weighDeterminers)
                logProbability1 = round(Decimal(class1Prediction).log10()/Decimal(2).log10(), 4)
                logProbability2 = round(Decimal(class2Prediction).log10()/Decimal(2).log10(), 4)
                actual = line.split()[0]
                if logProbability1 > logProbability2:
                    prediction = class1.name
                    predictionOutputFile.write("Prediction: " + prediction + " Actual: " + actual + " | " + class1.name + " Probability: " + str(logProbability1) + " " + class2.name + " Probability: " + str(logProbability2) + "\n")
                else:
                    prediction = class2.name
                    predictionOutputFile.write("Prediction: " + prediction + " Actual: " + actual + " | " + class1.name + " Probability: " + str(logProbability1) + " " + class2.name + " Probability: " + str(logProbability2) + "\n")
                predictionCount += 1
                if prediction == actual:
                    accurateCount += 1
            accurracy = Decimal(accurateCount)/predictionCount
            predictionOutputFile.write(str(accurracy * 100) + "% accurate")

 # Get the prediction for an individual review  
def getPrediction(line, predictionClass, weighDeterminers):
    determiners = ["the", "a", "an", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their", "she", "he", "they", "them"]
    line = line.strip()
    words = line.split()
    words.pop(0)
    prediction = Decimal(predictionClass.priorProbability)
    for word in words:
        colonIndex = word.find(":")
        key = word[:colonIndex]
        value = int(word[colonIndex+1:len(word)])
        if weighDeterminers and key not in determiners:
            value += 5
        if key in predictionClass.bagOfWords:
            prediction *= predictionClass.AddOnProbability[key] ** value
        else:
            prediction *= predictionClass.unknownProbability ** value
    return prediction

trainParameterFile = sys.argv[1]
testParameterFile = sys.argv[2]
outputFile = sys.argv[3]

comedy = PreditcionClass("comedy")
action = PreditcionClass("action")
fillBag("movie-review-small.nb", comedy, action)
findProbabilities(comedy, 1)
findProbabilities(action, 1)
calculatePredictions("movie-review-small-test.txt", comedy, action, "output-small.txt", False)

pos = PreditcionClass("pos")
neg = PreditcionClass("neg")
fillBag(trainParameterFile, pos, neg)
findProbabilities(pos, 1)
findProbabilities(neg, 1)
calculatePredictions(testParameterFile, pos, neg, outputFile, True)