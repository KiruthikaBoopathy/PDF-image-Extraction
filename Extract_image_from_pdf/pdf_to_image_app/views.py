import os
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import CreateAPIView
import fitz
from .models import FileUpload
from .serializers import FileUploadSerializer


class UploadedFileCreateAPIView(CreateAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        pdf_path = instance.pdf_file.path

        image_paths = self.extract_images_from_pdf(pdf_path)
        if len(image_paths) == 0:
            image_response = "No images in PDF"
        else:
            image_response = image_paths

        return JsonResponse({'image_paths': image_response, 'pdf_file': serializer.data, 'pdf_path': pdf_path})

    def extract_images_from_pdf(self, pdf_path):
        image_paths = []

        output_folder = r'C:\Users\Vrdella\Downloads\images'

        try:
            pdf_file = fitz.open(pdf_path)
            page_count = pdf_file.page_count
            images_list = []
            for page_num in range(page_count):
                page_content = pdf_file[page_num]
                images_list.extend(page_content.get_images())

            if len(images_list) == 0:
                raise ValueError(f'No images found in {pdf_path}')

            for i, img in enumerate(images_list, start=1):
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image['image']
                image_ext = base_image['ext']
                image_name = str(i) + '.' + image_ext
                image_path = os.path.join(output_folder, image_name)
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_bytes)

                image_paths.append(image_path)

        except Exception as e:
            print(f"Error extracting images from PDF: {e}")

        finally:
            pdf_file.close()

        return image_paths
