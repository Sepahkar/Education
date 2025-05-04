import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Config.settings')
django.setup()

from EducationApp import generate_data

if __name__ == '__main__':
    generate_data.generate_sample_data()