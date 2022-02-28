
mappingXX = {1: ["'"], 2: ["a", "b", "c"], \
           3: ["d", "e",  "f"], \
           4: ["g","h", "i"], \
           5: ["j", "k", "l"], \
           6: ["m", "n", "o"], \
           7: ["p","q", "r", "s"], \
           8: ["t", "u", "v"], \
           9: ["w", "x", "y", "z"]}

def runNumber(my_inputs):
    print("The number being input is：",my_inputs)

def runLetter(my_inputs,inputTrue,biao):
    letter=mappingXX[inputTrue]
    weiShu=len(letter)
    if biao==weiShu:
        biao=0
    print("The letter being input is ",letter[biao]," of ",letter)


