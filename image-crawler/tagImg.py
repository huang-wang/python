import os
def tagFile(dirPath):
    if os.path.exists(dirPath):
        print('start to process !')
        for parent, dirnames, filenames in os.walk(dirPath):
            for dirname in dirnames:
                print('dirname is %s' % dirname)
                for parent, dirnames, filenames in os.walk(dirPath+"/"+dirname):
                    count = 0
                    for filename in filenames:
                        print('filename is %s' % filename)
                        print(dirPath+"/"+dirname+"/"+filename)
                        print(dirPath+"/"+dirname +"1/"+dirname+str(count)+".png")
                        os.rename(dirPath+"/"+dirname+"/"+filename, dirPath+"/"+dirname +"1/"+dirname+str(count)+".png")
                        count = count + 1
        print('task done')

tagFile('data')