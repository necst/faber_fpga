# /******************************************
# *MIT License
# *
# *Copyright (c) [2022] [Eleonora D'Arnese, Davide Conficconi, Emanuele Del Sozzo, Luigi Fusco, Donatella Sciuto, Marco Domenico Santambrogio]
# *
# *Permission is hereby granted, free of charge, to any person obtaining a copy
# *of this software and associated documentation files (the "Software"), to deal
# *in the Software without restriction, including without limitation the rights
# *to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# *copies of the Software, and to permit persons to whom the Software is
# *furnished to do so, subject to the following conditions:
# *
# *The above copyright notice and this permission notice shall be included in all
# *copies or substantial portions of the Software.
# *
# *THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# *IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# *FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# *AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# *LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# *OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# *SOFTWARE.
# ******************************************/

def binarize(img, soglia):
    img[img>=soglia]=255
    img[img<soglia]=0
    return(img)


def correct(i):
    gamma_corrected = exposure.adjust_log(i, 0.8)
    return(gamma_corrected)


def distances(g,t):
    g_t=np.asarray(g).astype(np.bool)
    t_t=np.asarray(t).astype(np.bool)
    di=1-(distance.dice(g_t.ravel(),t_t.ravel()))
    ja=1-(distance.jaccard(g_t.ravel(),t_t.ravel()))
    return(di,ja)


def IoU(g,t):
    overlap = g & t # Logical AND
    union = g | t # Logical OR
    IOU = overlap.sum()/float(union.sum()) 
    return(IOU)


def diff_pixel(g,t):
    tot=0
    for i in range(512):
        for j in range(512):
            if g[i][j]==t[i][j]:
                tot=tot+1
    tot1=(tot/(512*512))*100
    return(tot1)

import argparse
from skimage import exposure
from scipy.spatial import distance
import cv2
import matplotlib.pyplot as plt
import pydicom
import glob
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description='Iron software for res analysis onto a python env')
parser.add_argument("-f", "--flag", nargs='?', type=int, help='0 Read png images, 1 read dcm', default=0)
parser.add_argument("-tg", "--threshold_g", nargs='?', help='Threshold of G', default=2)
parser.add_argument("-tt", "--threshold_t", nargs='?', help='Threshold of T', default=2)
parser.add_argument("-rg", "--res_gold_path", nargs='?', help='Path of the Golden Results', default='./')
parser.add_argument("-rt", "--res_test_path", nargs='?', help='Path of the Results to compare against gold', default='./')
parser.add_argument("-l", "--label", nargs='?', help='prefix of the final file name', default='mat')
parser.add_argument("-rp", "--res_path", nargs='?', help='path of where store the results', default='./')

args = parser.parse_args()
flag=args.flag
soglia_g=args.threshold_g
#def 2
soglia_t=args.threshold_t
#def 3
res_gold_path = args.res_gold_path
res_test_path = args.res_test_path
prefix = args.res_path+"/gold-"+args.label+"-"
print(res_gold_path)
print(res_test_path)

dice=[]
jaccard=[]
acc=[]
curr_g_nmbr=[]
curr_test_nmbr=[]
Iou=[]




Gold=glob.glob(res_gold_path+'*.dcm')
if flag==0:
   Test=glob.glob(res_test_path+'*.png')
else:
   Test=glob.glob(res_test_path+'*.dcm')


Gold.sort()
Test.sort()
print(Gold)
print(Test)

for i,j in zip(Gold, Test):
    print(i)
    print(j)
    
    curr_g_nmbr.append(((i.split('/')).pop()).split('.')[0][2:5])
    curr_test_nmbr.append(((j.split('/')).pop()).split('.')[0][2:5])

    g=pydicom.dcmread(i)
    go=g.pixel_array
    gold=cv2.normalize(go, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)   
    
    if flag==0:
        test=cv2.imread(j,0)
    else:
        t=pydicom.dcmread(j)
        te=t.pixel_array
        test=cv2.normalize(te, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)  
    
    gold_cor=correct(gold)
    test_cor=correct(test)
    
    gold_bin=binarize(gold_cor,soglia_g)
    test_bin=binarize(test_cor,soglia_t)
    
    d=distances(gold_bin,test_bin)
    iou=IoU(gold_bin,test_bin)
    n_pix_diff=diff_pixel(gold_bin,test_bin)
    
    dice.append(d[0])
    jaccard.append(d[1])
    Iou.append(iou)
    acc.append(n_pix_diff)

df = pd.DataFrame(list(zip(*[Iou, acc])),columns=['IoU', 'Accuracy'])
df.to_csv(prefix+'score_results.csv', index=False)