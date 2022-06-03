from sklearn.metrics import confusion_matrix
import itertools
import matplotlib.pyplot as plt 
import numpy as np 
import csv

# increase font size
plt.rcParams.update({'font.size': 14})


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          fname='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        divisor =  cm.sum(axis=1)[:, np.newaxis]
        for i in range(len(divisor)):
            if divisor[i][0] == 0:  # prevent dividing by 0
                divisor[i][0] = 1
        cm = cm.astype('float') / divisor 
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    # plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.1f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, format(cm[i, j]*100, fmt) + '%',
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")    
        
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig(fname, bbox_inches='tight', pad_inches=0.3)


# get y_test_true and predictions
OS_classify = {
    "windows": 0,
    "linux": 1,
    "unknown": 2
}
browser_classify = {
    "chrome": 0,
    "edge": 1,
    "chromium": 2,
    "firefox": 3,
    "unknown": 4
}
browser_translate = {  # make chrome, edge, chromium all point to same value 
    0: 0,
    1: 0,
    2: 0,
    3: 1
}
traffic_classify = {
    "browsing": 0,
    "streaming_youtube": 1,
    "streaming_twitch": 2,
    "unknown": 3
}
class_names_lst = [ ["windows", "linux"], ["chrome", "edge", "firefox"], ["browsing", "youtube", "twitch"] ] 
class_index = 2
class_names = class_names_lst[class_index]

# Compute confusion matrix
cnf_matrix = np.array([[71,1,2], [0,73,0], [2,0,67]])
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names,
                      title='Confusion matrix without normalization',
                      fname='Confusion_matrix_without_normalization')

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                      title='Confusion matrix with normalization',
                      fname='Normalized_confusion_matrix')

plt.show()