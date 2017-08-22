#split the database to train/val/test
import os

dirPath='dadd'
for parent, dirnames, filenames in os.walk(dirPath):
    for dirname in dirnames :
        for parent, dirnames, filenames in os.walk(dirPath + '/' +dirname):
            totalcount = len(filenames)
            print(totalcount)
            destPath = 'train/'
            count = 0
            for filename in filenames:
                filePath = dirPath+'/'+dirname+'/'+filename
                print(destPath + filename)
                os.rename(filePath, destPath + filename)
                count += 1
                print(count)
                # if count > totalcount*0.8 :
                    # if count > totalcount*0.9 :
                        # destPath = 'test/'  
                    # else:
                        # destPath = 'val/' 
                if count > totalcount*0.9 :
                    destPath = 'test/'  
                    