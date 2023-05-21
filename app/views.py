import boto3
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.views.generic import TemplateView
from storages.backends.s3boto3 import S3Boto3Storage


class IndexView(TemplateView):
    template_name = "app/index.html"


# TODO: 画像の保存時のファイル名を変更する。

class UploadView(TemplateView):
    template_name = "app/upload_file.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    from django.core.files.base import ContentFile

    def post(self, request, *args, **kwargs):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
        s3_bucket = S3Boto3Storage(bucket_name=settings.AWS_STORAGE_BUCKET_NAME)

        try:
            file_obj = request.FILES['file']
        except KeyError:
            return render(request, self.template_name, {'error_message': 'No file selected.'})

        if not s3_bucket.file_overwrite:
            if s3.head_object(Bucket=s3_bucket, Key=file_obj.name):
                return render(request, self.template_name, {'error_message': 'File already exists.'})

        file_content = ContentFile(file_obj.read())
        s3.upload_fileobj(file_content, s3_bucket.bucket_name, file_obj.name)

        return render(request, self.template_name, {'success_message': 'File uploaded successfully.'})


class ExtractView(TemplateView):
    template_name = "app/extract_text.html"

    def post(self, request, *args, **kwargs):
        s3 = boto3.client('s3')
        s3_bucket = S3Boto3Storage(bucket=settings.AWS_STORAGE_BUCKET_NAME)
        file_obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key='<アップロードされたファイルのS3キー>')
        file_content = file_obj['Body'].read()
        textract = boto3.client('textract')
        response = textract.detect_document_text(Document={'Bytes': file_content})
        text = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                text += item["Text"] + "\n"
        return render(request, self.template_name, {'text': text})
