import csv 

# accuracy scores 
OS_acc = {
    "correct": 0,
    "wrong": 0,
    "unknown": 0 
}
browser_acc = {
    "correct": 0,
    "wrong": 0,
    "unknown": 0 
}
traffic_acc = {
    "correct": 0,
    "wrong": 0,
    "unknown": 0 
}

# classification matching
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
traffic_classify = {
    "browsing": 0,
    "streaming_youtube": 1,
    "streaming_twitch": 2,
    "unknown": 3
}
OS_classify_inv = {v: k for k, v in OS_classify.items()}
browser_classify_inv = {v: k for k, v in OS_classify.items()}
traffic_classify_inv = {v: k for k, v in OS_classify.items()}

# read predictions 
with open('CSVs/dataset_splitted_predictions_manual_new_pred_strategy.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        OS_tuple = (int(row[0]),  int(row[1]))
        browser_tuple = (int(row[3]),  int(row[4]))
        traffic_tuple = (int(row[6]),  int(row[7]))
        
        # OS
        if OS_tuple[1] == OS_classify["unknown"]:
            OS_acc["unknown"] += 1
        elif OS_tuple[1] == OS_tuple[0]:
            OS_acc["correct"] += 1
        else:
            OS_acc["wrong"] += 1

        # browser
        if browser_tuple[1] == browser_classify["unknown"]:
            browser_acc["unknown"] += 1
        elif browser_tuple[1] == browser_classify["firefox"] and browser_tuple[0] != browser_classify["firefox"]:
            browser_acc["wrong"] += 1
        elif browser_tuple[0] == browser_classify["firefox"] and browser_tuple[1] != browser_classify["firefox"]:
            browser_acc["wrong"] += 1
        else:
            browser_acc["correct"] += 1

        # traffic 
        if traffic_tuple[1] == traffic_classify["unknown"]:
            traffic_acc["unknown"] += 1
        elif traffic_tuple[0] == traffic_tuple[1]:
            traffic_acc["correct"] += 1
        else:
            traffic_acc["wrong"] += 1

print(OS_acc)
print(browser_acc)
print(traffic_acc)
print(f"OS accuracy WITHOUT unknown: {float(OS_acc['correct']) / float(OS_acc['correct'] + OS_acc['wrong'])}")
print(f"OS accuracy WITH unknown: {float(OS_acc['correct']) / float(OS_acc['correct'] + OS_acc['wrong'] + OS_acc['unknown'])}")
print(f"Browser accuracy: {float(browser_acc['correct']) / float(browser_acc['correct'] + browser_acc['wrong'])}")
print(f"Traffic accuracy: {float(traffic_acc['correct']) / float(traffic_acc['correct'] + traffic_acc['wrong'])}")


"""
{'correct': 554, 'wrong': 15, 'unknown': 444}                                                                           
{'correct': 891, 'wrong': 122, 'unknown': 0}                                                                            
{'correct': 917, 'wrong': 96, 'unknown': 0}                                                                             
OS accuracy WITHOUT unknown: 0.9736379613356766                                                                         
OS accuracy WITH unknown: 0.5468904244817374                                                                            
Browser accuracy: 0.8795656465942744                                                                                    
Traffic accuracy: 0.9052319842053307 
"""