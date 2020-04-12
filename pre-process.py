from decimal import *
from math import log
import os
import re
import sys

# Put all the words from the vocabulary into a string
def getVocab(reviewDirectory):
    vocab = "Vocabulary "
    with open(reviewDirectory + "/aclimdb/imdb.vocab", 'r') as vocabFile:
         for line in vocabFile:
             vocab += line.strip() + " "
    vocab += ("\n")
    return vocab

# Add the Vocabulary to the parameter file
def outputVocab(outputFile, vocab):
    with open(outputFile, "a") as parameterFile:
        parameterFile.write(vocab)

# Process the files in the given directory
def processFiles(files, path, type, reviewFile, outputFile):
    fileCount = 0
    with open(reviewFile, "a") as trainingFile:
        for file in files:
            fileCount += 1
            with open(path + "/" + file, 'r') as currentFile:
                for line in currentFile:
                    newLine = tokenizeLine(line)
                    vectorizeParameters(type, newLine, outputFile)
                    trainingFile.write(newLine + "\n")
            trainingFile.write("-----------------------------------------------\n")
    return fileCount

# Seperate punctuation and lowercase all letters
def tokenizeLine (line):
    line = line.lower()
    splitLine = re.findall(r"[\w']+|[.,!?;\"]", line)
    newLine = ""
    for token in splitLine:
        newLine += token + " "
    return newLine

# Turn a review into a vector of parameters
def vectorizeParameters(type, line, outputFile):
    parameters = {}
    words = line.split()
    for word in words:
        word = word.strip()
        if word not in parameters:
            parameters[word] = 1
        else:
            parameters[word] += 1
    outputParameters(type, parameters, outputFile)

# Add parameters to the output file
def outputParameters(type, parameters, outputFile):
    with open(outputFile, "a") as parameterFile:
        if parameters:
            parameterFile.write(type + " ")
        for key, value in parameters.items():
            parameterFile.write(key + ":" + str(value) + " ")
        parameterFile.write("\n")

# Get and output prior probabilities
def outputPriorProbabilities(posCount, negCount, outputFile):
    totalCount = posCount + negCount
    posPrior = Decimal(posCount)/totalCount
    negPrior = Decimal(negCount)/totalCount
    with open(outputFile, "a") as parameterFile:
        parameterFile.write("Prior-Probabilities pos:" + str(posPrior) + " neg:" + str(negPrior))
         
reviewDirectory = sys.argv[1]
vocabulary = getVocab(reviewDirectory)

outputVocab("movie-review-BOW.nb", vocabulary)
posTrainDirectory = reviewDirectory + "/aclimdb/train/pos"
posTrainFiles = os.listdir(posTrainDirectory)
posFileCount = processFiles(posTrainFiles, posTrainDirectory, "pos", "posTraining.txt", "movie-review-BOW.nb")
negTrainDirectory = reviewDirectory + "/aclimdb/train/neg"
negTrainFiles = os.listdir(negTrainDirectory)
negFileCount = processFiles(negTrainFiles, negTrainDirectory, "neg", "negTraining.txt", "movie-review-BOW.nb")
outputPriorProbabilities(posFileCount, negFileCount, "movie-review-BOW.nb")

posTestDirectory = reviewDirectory + "/aclimdb/test/pos"
posTestFiles = os.listdir(posTestDirectory)
processFiles(posTestFiles, posTestDirectory, "pos", "posTesting.txt", "testParameters.txt")
negTestDirectory = reviewDirectory + "/aclimdb/test/neg"
negTestFiles = os.listdir(negTestDirectory)
processFiles(negTestFiles, negTestDirectory, "neg", "negTesting.txt", "testParameters.txt")