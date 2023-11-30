from django.db import models


class FileUpload(models.Model):
    pdf_file = models.FileField(upload_to='pdfs/')
