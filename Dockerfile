FROM python:3.12
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "rin.py", "--server.port=8501", "--server.address=0.0.0.0"]