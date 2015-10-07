import os,sys,pdb,pickle,cv2
import numpy as np
from sklearn.lda import LDA
from sklearn.decomposition import PCA
import image_gabor_feature as igbf

def LDA_A(rootdir, posdir, posnum, negnum_p):
    pos = []
    neg = [] 
    pathpos = []
    pathneg = []
    folders = []
    imgspos = []
    imgsneg = []
    with open('list.txt', 'r') as f:
        for line in f:
            line = line.strip()
            folders.append(line)
    gbf = igbf.GABOR_FEAT()
    for folder in folders:
        fname = os.path.join(rootdir, folder)
        if 0 == cmp(folder, posdir):
            fvs,imgs = gbf.gen_folder_gabor(fname, posnum)
            if fvs is None:
                print 'pos None ',fname
                continue
            pos.extend(fvs)
            imgspos.extend(imgs)
            pathpos.extend([folder for k in range(len(fvs))])
        else:
            fvs,imgs = gbf.gen_folder_gabor(fname, negnum_p)
            if fvs is None:
                print 'neg None ', fname
                continue
            neg.extend(fvs)
            imgsneg.extend(imgs)
            pathneg.extend([folder for k in range(len(fvs))])
    label0 = [0 for k in range(len(pos))]
    label1 = [1 for k in range(len(neg))]
    samples = np.array(pos + neg)
    labels = np.array(label0 + label1)
    paths = pathpos + pathneg
    imgs = imgspos + imgsneg
    clf = PCA(300)
    samples = clf.fit_transform(samples)
    print 'after pca : ', samples.shape
    clf = LDA()
    clf.fit(samples,labels)
    cnf = clf.decision_function(samples)
    X = []

    for k in range(len(paths)):
        X.append((paths[k], cnf[k], imgs[k]))
    X = sorted(X, key = lambda a : a[1])
    line = ""
    lineA = "" #sometimes, the positive set is split into two parts
    lineB = ""
    for path, cnf, img in X:
        line += str(cnf) + ' ' + path + ' ' + img + '\n'
        if 0 != cmp(path, posdir):
            continue
        if cnf > 0:
            lineA += img + '\n'
        else:
            lineB += img + '\n'

    with open('A.txt', 'w') as f:
        f.writelines(lineA)
    with open('B.txt', 'w') as f:
        f.writelines(lineB)

    with open('result.txt', 'w') as f:
        f.writelines(line) 

    return 


def LDA_B(rootdir, folderA, folderB, folderC):
    pos = []
    neg = [] 
    imgspos = []
    imgsneg = []
    gbf = igbf.GABOR_FEAT()

    #1--class A
    fvs, imgs = gbf.gen_folder_gabor(os.path.join(rootdir, folderA), 100000)
    pos.extend(fvs)
    imgspos.extend(imgs)
    #2--class B
    fvs, imgs = gbf.gen_folder_gabor(os.path.join(rootdir, folderB), 100000)
    neg.extend(fvs)
    imgsneg.extend(imgs)

    #3--train
    label0 = [0 for k in range(len(pos))]
    label1 = [1 for k in range(len(neg))]
    samples = np.array(pos + neg)
    labels = np.array(label0 + label1)
    imgs = imgspos + imgsneg
    clf_pca = PCA(300)
    samples = clf_pca.fit_transform(samples)
    print 'after pca : ', samples.shape
    clf_lda = LDA()
    clf_lda.fit(samples,labels)


    #4--predict
    fvs, imgs = gbf.gen_folder_gabor(os.path.join(rootdir, folderC), 100000)
    samples = np.array(fvs) 
    samples = clf_pca.transform(samples)
    cnf = clf_lda.decision_function(samples)
    X = []
    for k in range(len(imgs)):
        X.append((cnf[k], imgs[k]))
    X = sorted(X, key = lambda a : a[0])
    lineA = "" #sometimes, the positive set is split into two parts
    lineB = ""
    for cnf, img in X:
        if cnf > 0:
            lineA += img + '\n'
        else:
            lineB += img + '\n'

    with open('A.txt', 'w') as f:
        f.writelines(lineA)
    with open('B.txt', 'w') as f:
        f.writelines(lineB)
    return 



if __name__=="__main__":
    if len(sys.argv) == 0:
        with open('config.txt','r') as f:
            rootdir = f.readline().strip()
            posdir = f.readline().strip()
            posnum = np.int64(f.readline().strip())
            negnum_p = np.int64(f.readline().strip())
        LDA_A(rootdir, posdir, posnum, negnum_p)
    elif len(sys.argv) == 5:
        rootdir = sys.argv[1]
        folderA = sys.argv[2]
        folderB = sys.argv[3]
        folderC = sys.argv[4]
        LDA_B(rootdir, folderA, folderB, folderC)
    else:
        print 'unknown options'





