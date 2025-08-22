from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import os
from django.core.files.storage import FileSystemStorage
import pickle
import os
from keras.models import Sequential, load_model, Model
from keras.layers import AveragePooling2D, Dropout, Flatten, Dense, Input, Activation
from keras.optimizers import Adam
from keras.layers import  MaxPooling2D
from keras.layers import Convolution2D
from lime import lime_image
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt
import cv2
import numpy as np
import io
import base64

global username
explainer = lime_image.LimeImageExplainer()

#get Grad Cam Image
def getGradCam(img, model):
    feature_model = Model(model.inputs, model.layers[-7].output)
    predict = feature_model.predict(img)#now using  cnn model to detcet tumor damage
    predict = predict[0]
    pred = predict[:,:,24]
    pred =  pred*255
    pred = cv2.resize(pred, (150, 150))
    return pred

#function to classify image as fake or real
def classifyImage(image_path, nasnet_model):
    image = cv2.imread(image_path)
    img = cv2.resize(image, (32,32))
    im2arr = np.array(img)
    im2arr = im2arr.reshape(1,32,32,3)
    img = np.asarray(im2arr)
    img = img.astype('float32')
    img = img/255
    predict = nasnet_model.predict(img)
    predict = np.argmax(predict)
    status = "Real"
    if predict == 0:
        status = "Fake"
    grad_cam = getGradCam(img, nasnet_model)
    # Generate Lime explanation
    explanation = explainer.explain_instance(img[0], nasnet_model.predict)
    # Visualize the explanation
    temp, mask = explanation.get_image_and_mask(explanation.top_labels[0], positive_only=True, num_features=5, hide_rest=False)
    lime_marking = mark_boundaries(temp / 2 + 0.5, mask)
    lime_marking = cv2.resize(lime_marking, (150, 150), interpolation=cv2.INTER_LANCZOS4)
    image = cv2.imread(image_path)
    image = cv2.resize(image, (150, 150))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #lime_marking = cv2.cvtColor(lime_marking, cv2.COLOR_BGR2RGB)
    cv2.putText(image, status, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), 2)
    f, axarr = plt.subplots(1,3, figsize=(8,4)) 
    axarr[0].imshow(image)
    axarr[0].title.set_text("Input Image")
    axarr[1].imshow(grad_cam)
    axarr[1].title.set_text('Grad Cam Image')
    axarr[2].imshow(lime_marking)
    axarr[2].title.set_text('Lime Explanation Image')
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    return img_b64

def SingleImage(request):
    if request.method == 'GET':
       return render(request, 'SingleImage.html', {})

def SingleImageAction(request):
    if request.method == 'POST':
        global uname, labels
        filename = request.FILES['t1'].name
        image = request.FILES['t1'].read() #reading uploaded file from user
        if os.path.exists("DetectionApp/static/"+filename):
            os.remove("DetectionApp/static/"+filename)
        with open("DetectionApp/static/"+filename, "wb") as file:
            file.write(image)
        file.close()
        model = load_model("model/nasnet_weights.hdf5")
        img_b64 = classifyImage("DetectionApp/static/"+filename, model)
        context= {'data':"Detection Output", 'img': img_b64}
        return render(request, 'UserScreen.html', context)   

def UserLoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Welcome '+username}
            return render(request, "UserScreen.html", context)
        else:
            context= {'data':'Invalid username'}
            return render(request, 'UserLogin.html', context)

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

