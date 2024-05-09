import base64
from config import s3
from typing import List, Tuple


def get_photo(post_id: int) -> str:
    bucket_name = 'cyberbucket-s3'
    prefix = f'post-{post_id}.'
    
    try:
        # Pobranie listy obiektów w bucketcie S3 z danym prefixem
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        # Wybór pierwszego obiektu pasującego do prefixu
        if 'Contents' in response:
            first_object = response['Contents'][0]
            file_key = first_object['Key']
            
            # Pobranie zawartości pliku z S3
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
            photo_data = response['Body'].read()
            photo_data_base64 = base64.b64encode(photo_data).decode('utf-8')
            return photo_data_base64
        else:
            # Jeśli nie ma pasujących obiektów
            print("No objects found with the specified prefix.")
            return None
    except Exception as e:
        # Obsługa błędów
        print(f"An error occurred: {e}")
        return None
    


def get_photos_in_range(post_ids: List[int]) -> List[Tuple[int, str]]:
    photos = []  # Lista zawierająca krotki (post_id, photo_data_base64)
    bucket_name = 'cyberbucket-s3'
    prefix = 'post-'  # Prefiks wspólny dla wszystkich obiektów
    try:
        # Pobranie listy obiektów w bucketcie S3 z danym prefiksem
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        # Iteracja przez wszystkie obiekty z odpowiedzi
        for obj in response.get('Contents', []):
            key = obj['Key']
            
            # Sprawdzenie, czy obiekt pasuje do któregoś z id postów
            for post_id in post_ids:
                if f'post-{post_id}.' in key:
                    # Pobranie zawartości pliku z S3
                    response = s3.get_object(Bucket=bucket_name, Key=key)
                    photo_data = response['Body'].read()
                    photo_data_base64 = base64.b64encode(photo_data).decode('utf-8')
                    photos.append((photo_data_base64, post_id)) 
        return photos

    except Exception as e:
        # Obsługa błędów
        print(f"An error occurred: {e}")
        return None

    



