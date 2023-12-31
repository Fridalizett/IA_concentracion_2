# -*- coding: utf-8 -*-
"""CNN_MOD2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uRZMIf0TtrJW_HhwzxB5CCieIDXlnfFo
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras import layers, models
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from google.colab import drive

'''
def mount_google_drive():
    # Montar Google Drive
    drive.mount('/content/gdrive')
'''

def set_paths():
    # Rutas de las carpetas
    drive_path = '/content/gdrive/MyDrive/Entregable'
    images_path = os.path.join(drive_path, "images")

    train_path = os.path.join(images_path, "train")
    test_path = os.path.join(images_path, "test")
    validation_path = os.path.join(images_path, "validation")

    return train_path, test_path, validation_path

def load_pretrained_model():
    # Descargar y cargar el modelo preentrenado VGG16 sin incluir las capas densas superiores
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    # Congelar las capas convolucionales para que no se actualicen durante el entrenamiento
    for layer in base_model.layers:
        layer.trainable = False

    return base_model

def create_model(base_model, num_classes=10):
    # Crear el modelo completo, se añadieron las capas personalizadas, de clasificación y droput
    model = models.Sequential()
    model.add(base_model)
    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(num_classes, activation='softmax'))

    # Compilar el modelo
    from tensorflow.keras.optimizers import Adam
    model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

    return model

def create_data_generators(train_path, validation_path):
    # Crear generadores de datos para train y val
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2
    )

    test_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        shuffle=True
    )

    validation_generator = test_datagen.flow_from_directory(
        validation_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        shuffle=False
    )

    return train_generator, validation_generator

def train_model(model, train_generator, validation_generator, epochs=50):
    # Entrenar el modelo
    history = model.fit(train_generator, epochs=epochs, validation_data=validation_generator)

    # Graficar la pérdida y la precisión durante el entrenamiento
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

def evaluate_model(model, validation_generator):
    # Evaluar el modelo
    y_true = validation_generator.classes

    # Obtener predicciones como probabilidades
    y_pred_prob = model.predict(validation_generator)

    # Convertir las predicciones de probabilidades a clases
    y_pred = np.argmax(y_pred_prob, axis=1)

    # Obtener nombres de clases
    class_names = list(validation_generator.class_indices.keys())

    # Matriz de confusión
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

    # Resultados
    print(classification_report(y_true, y_pred, target_names=class_names))

    # Imprimir resumen del modelo
    model.summary()

    # Guardar el modelo
    model.save('model_.h5')


def evaluate_on_test_set(model, test_generator):
    # Crear generador de datos para test
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        test_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',  # Multiclase
        shuffle=False
    )

    # Evaluar el modelo con test
    test_results = model.evaluate(test_generator)

    print("Test Loss:", test_results[0])
    print("Test Accuracy:", test_results[1])

    # Obtener predicciones en probabilidades
    y_test_true = test_generator.classes
    y_test_pred_prob = model.predict(test_generator)

    # Convertir las predicciones de probabilidades a clases
    y_test_pred = np.argmax(y_test_pred_prob, axis=1)

    # Obtener nombres de clases
    class_names_test = list(test_generator.class_indices.keys())

    # Mmatriz de confusión test
    cm_test = confusion_matrix(y_test_true, y_test_pred)
    sns.heatmap(cm_test, annot=True, fmt="d", cmap="Blues", xticklabels=class_names_test, yticklabels=class_names_test)
    plt.title('Test Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

    # Resultados
    print(classification_report(y_test_true, y_test_pred, target_names=class_names_test))

    # Imágenes de predicciones
    sample_images_test, sample_labels_test = next(test_generator)

    for i in range(len(sample_labels_test)):
        plt.imshow(sample_images_test[i])
        true_label_idx_test = np.argmax(sample_labels_test[i])
        true_label_test = class_names_test[true_label_idx_test]
        pred_prob_test = model.predict(np.expand_dims(sample_images_test[i], axis=0))[0]
        pred_label_test = class_names_test[np.argmax(pred_prob_test)]
        plt.title(f'True: {true_label_test}, Predicted: {pred_label_test} ({pred_prob_test.max():.2f})')
        plt.show()

def predict_from_image(model, image_path):
    from tensorflow.keras.preprocessing import image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalizar la imagen

    # Obtener predicciones como probabilidad
    predictions = model.predict(img_array)

    # Convertir las predicciones de probabilidades a clases
    predicted_class = np.argmax(predictions)

    # Obtener el nombre de la clase predicha
    class_names = list(validation_generator.class_indices.keys())
    predicted_class_name = class_names[predicted_class]

    # Imprimir la imagen y predicción
    plt.imshow(img)
    plt.title(f'Predicted class: {predicted_class_name} ({predictions[0][predicted_class]:.2%})')
    plt.show()

'''
# Montar Google Drive
mount_google_drive()

# Obtener rutas
train_path, test_path, validation_path = set_paths()

# Cargar modelo preentrenado
base_model = load_pretrained_model()

# Crear modelo completo
model = create_model(base_model)

# Crear generadores de datos
train_generator, validation_generator = create_data_generators(train_path, validation_path)

# Entrenar modelo
train_model(model, train_generator, validation_generator)

# Evaluar modelo en conjunto de validación
evaluate_model(model, validation_generator)

# Evaluar modelo en conjunto de prueba
evaluate_on_test_set(model, test_path)

'''

from tensorflow.keras.models import load_model
# Ruta del el modelo
model_path = '/content/model_.h5'
# Cargar el modelo
loaded_model = load_model(model_path)

# Llamada a la función con la ruta de la imagen a predecir
image_path_to_predict = '/content/bloodstone.jpg'
predict_from_image(loaded_model, image_path_to_predict)