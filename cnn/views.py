import numpy as np
from django.http import JsonResponse
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
import tensorflow as tf
import os
from django.db import connection
import json

MODEL_APP = os.path.join(os.path.dirname(__file__), 'model' , 'my_model.keras')

# Global variable to store the model (loaded once)
model = tf.keras.models.load_model(MODEL_APP)  # Load model at startup

# Class names (assumed for prediction)
class_names = ['gado - gado', 'pecel', 'rujak']

@csrf_exempt
def predict_image(request):
    img_height = 180  # Target image height
    img_width = 180  # Target image width

    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Load the uploaded image
            uploaded_file = request.FILES['image']
            image = Image.open(uploaded_file)

            # Convert the image to a numpy array and normalize it
            img = image.resize((img_width, img_height))  # Resize to model input size
            img_array = tf.keras.utils.img_to_array(img)  # Convert to array
            img_array = tf.expand_dims(img_array, 0)  # Add batch dimension

            # Perform the prediction using the preloaded model
            predictions = model.predict(img_array)
            score = tf.nn.softmax(predictions[0])

            # Get the predicted class and confidence
            predicted_class = class_names[np.argmax(score)]
            confidence = 100 * np.max(score)

            # Return the prediction result where resep_name from resep has same name with predicted_class
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM resep WHERE nama_resep LIKE %s
                    """, [f"%{predicted_class}%"])
                resep = cursor.fetchall()

                resep_list = []

                for row in resep:    
                    resep_list.append({
                        'id': row[0],
                        'nama_resep': row[1],
                        'deskripsi': row[2],
                        'bahan': row[3].split(','),
                        'cara_buat': row[4].split('-'),
                        'alat': row[5].split(','),
                        'image': row[6]
                    })

                return JsonResponse({
                    'predicted_class': predicted_class,
                    'resep': resep_list,
                })  

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def tambah_resep(request):
    if request.method == 'POST':
        try:
            # Parse JSON dari request body
            data = json.loads(request.body)

            # Ambil data dari request
            nama_resep = data.get('nama_resep')
            deskripsi = data.get('deskripsi')
            bahan = data.get('bahan')
            cara_buat = data.get('cara_buat')
            alat = data.get('alat')
            image = data.get('image')

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO resep (nama_resep, deskripsi, bahan, cara_buat, alat, image)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [nama_resep, deskripsi, bahan, cara_buat, alat, image])

            return JsonResponse({'message': 'Resep berhasil ditambahkan!' + nama_resep}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# buat GET pada table resep
@csrf_exempt
def get_resep(request):
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM resep
                """)
                resep = cursor.fetchall()

                resep_list = []

                for row in resep:    
                    resep_list.append({
                        'id': row[0],
                        'nama_resep': row[1],
                        'deskripsi': row[2],
                        'bahan': row[3].split(','),
                        'cara_buat': row[4].split('-'),
                        'alat': row[5].split(','),
                        'image': row[6]
                    })

            return JsonResponse({'resep': resep_list})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

